module.exports = function() {
  var map, active = null, usedSearch = false, data = {}, blueIcon, darkBlueIcon, redIcon, markers, mapboxToken = 'pk.eyJ1Ijoib3VycmV2b2x1dGlvbiIsImEiOiJjaXpzdm91M3UwMDA3MzNvY2NhZXZtZ21hIn0.WBmvgFv12o8eEnv2GsZthA';

  function init(mapDiv) {
    initMap(mapDiv);
  }

  function initMap(mapDiv) {
    map = L.map(mapDiv).setView([37.8, -96.9], 4);

    var baseLayer = L.tileLayer('https://api.mapbox.com/styles/v1/ourrevolution/cj1tl1d07001h2slqtzp1o8s5/tiles/256/{z}/{x}/{y}?access_token=' + mapboxToken, {
        maxZoom: 18
      }
    ).addTo(map);

    blueIcon = L.divIcon({
      className: 'groups-map__icon blue',


      iconSize:     [16, 16], // size of the icon
      iconAnchor:   [0, 0], // point of the icon which will correspond to marker's location
      popupAnchor:  [8, 8] // point from which the popup should open relative to the iconAnchor
    });

    darkBlueIcon = L.divIcon({
      className: 'groups-map__icon dark-blue',


      iconSize:     [16, 16], // size of the icon
      iconAnchor:   [0, 0], // point of the icon which will correspond to marker's location
      popupAnchor:  [8, 8] // point from which the popup should open relative to the iconAnchor
    });

    redIcon = L.divIcon({
      className: 'groups-map__icon red',

      iconSize:     [16, 16], // size of the icon
      iconAnchor:   [0, 0], // point of the icon which will correspond to marker's location
      popupAnchor:  [8, 8] // point from which the popup should open relative to the iconAnchor
    });

    // TODO: implement clustering to avoid UX and performance issues with many dots on map
    // markers = L.markerClusterGroup({
    //   iconCreateFunction: function(cluster) {
		//      // return L.divIcon({ html: '<b>' + cluster.getChildCount() + '</b>' });
    //      return L.divIcon({
    //        className: 'groups-map__icon blue large',
    //
    //        iconSize:     [32, 32], // size of the icon
    //
    //        html: '<b>' + cluster.getChildCount() + '</b>'
    //      });
	  //    },
    //    maxClusterRadius: 40
    // });

    $(map).on('zoomend', function() {

      // only do this after user has used search box
      if (usedSearch) {
        getLocationsWithinBounds(map.getBounds());
      }
    });

    // populate(map);
  }

  function getAddress() {
    var geometry, place = autocomplete.getPlace();
    usedSearch = true;

    if (!place.geometry) {
      // TODO: Display this in .app__info
      return;
    } else {
      $('.groups-map__intro').addClass('collapsed');
      map.flyTo([place.geometry.location.lat(), place.geometry.location.lng()], 10, {duration:1});
    }
  }

  function positionMap(geometry) {
    map.flyTo(geometry, 10, {duration:1});
  }

  function monitorAPI(input) {
    var defaultPlaceholder = input.placeholder;

    setTimeout(function(){

        input.value = '';
        setInterval(function(){
          if(input.placeholder.indexOf('Oops') != -1){

            // undo Google grossness
            input.placeholder = defaultPlaceholder;
            input.removeAttribute('disabled');
            input.removeAttribute('style');
            input.classList.remove('gm-err-autocomplete');

            // kill events
            var clone = input.cloneNode(true);
            input.parentNode.replaceChild(clone, input);
          }
        }, 200);
    }, 500);
  }

  function addFeature(feature) {
    feature.addTo(map);
  }

  function paintGeoJson(geometry, options) {
    var feature = L.geoJson(geometry, options);

    feature.addTo(map);
  }

  function addGroup(group) {
    if (group.geometry!=null) {
      var coords = group.geometry.coordinates;
      var marker;

      if (group.properties.group_type == 1 || group.properties.group_type == 2) {
        // if State Organizing Committee  or State Chapter
        // color red and put on top layer
        marker = L.marker(coords.reverse(), {icon: redIcon, zIndexOffset: 1000})

      } else if (group.properties.group_type == 3) {
        // Dark blue icon for Campus Groups, middle layer
        marker = L.marker(coords.reverse(), {icon: darkBlueIcon, zIndexOffset: 100})

      } else {
        // Blue icon otherwise
        marker = L.marker(coords.reverse(), {icon: blueIcon});
      }

      marker.properties = group.properties;

      marker.bindPopup('<h4>'+ group.properties.name + '</h1><a href="/groups/'+ group.properties.slug +'/" class="component__cta btn btn-block btn-primary uppercase ls2">Get Involved</a>');

      marker.on('click touchstart', function() {
        updateInfo([this]);
      });

      marker.addTo(map);
    } else {
      console.log(group.properties.name + ' has no geometry.');
    }
  }

  function resetInfo() {
    $('.groups-map-info__status').html('');
  }

  function updateInfo(groups) {
    var location = '', city, county, state, country, group_type;

    resetInfo();

    if(groups.length != 0){
      for (var i=0; i<groups.length; i++) {
        city = groups[i].properties.city;
        county = groups[i].properties.county;
        state = groups[i].properties.state;
        country = groups[i].properties.country;

        if (country == 'US') {
          if (city && state) {
            location = city + ', ' + state;
          } else if (county && state) {
            location = county + ' County, ' + state;
          } else if (state) {
            location = state + ', ' + country ;
          } else {
            location = country;
          }
        } else {
          if (city && state) {
            location = city + ', ' + state + ', ' + country;
          } else if (county && state) {
            location = county + ' County, ' + state + ', ' + country;
          } else if (state) {
            location = state + ', ' + country ;
          } else if (city) {
            location = city + ', ' + country;
          } else {
            location = country;
          }
        }

        // TODO: show recurring meeting here instead
        description = groups[i].properties.description;
        group_type = groups[i].properties.group_type;

        // See GROUP_TYPES tuple in local groups model for group types
        if (group_type == 1) {
          group_type = 'State Organizing Committee';
        } else if (group_type == 2) {
          group_type = 'State Chapter';
        } else if (group_type == 3) {
          group_type = 'Campus Group';
        } else {
          group_type = null;
        }

        $('.groups-map-info__status').append('\
          <div class="component">\
            <div class="component__heading">\
              <span class="component__location">' + location + ((group_type) ? ' - ' + group_type : "") + '</span>\
              <h4 class="component__name">' + groups[i].properties.name  + '</h4>\
            </div>\
            <div class="component__info">\
              <a href="/groups/'+ groups[i].properties.slug + '/" class="component__cta btn btn-block btn-primary uppercase ls2">Get Involved</a>\
            </div> \
          </div>\
        ');
      }
    } else {
      $('.groups-map-info__status').append('\
        <div class="groups-map__add relative">\
        <h4 class="mt0">We couldn\'t find any groups here.</h4>\
        <p class="mb20">Try searching for a different city, zooming out, or using the buttons below to start your own group.</p>\
        <a href="https://docs.google.com/document/d/1BWp6HCZ6tngr6SJHJB3H1uPTX2Hcv6cMUQondCrBkHg/edit" class="btn btn-block btn-primary uppercase ls2" target="_blank" onclick="trackOutboundLink(\'https://docs.google.com/document/d/1BWp6HCZ6tngr6SJHJB3H1uPTX2Hcv6cMUQondCrBkHg/edit\', true)">Start a group</a>\
        <a href="/groups/new" class="btn btn-block btn-secondary uppercase ls2">Add your group</a>\
      </div>');
    }

  }

  function getLocationsWithinBounds(bounds) {
    var layers = [], t0 = performance.now();

    map.eachLayer(function (layer) {

      if(layer.properties) {
        if(bounds.contains(layer._latlng)) {
          layers.push(layer);
        }
      }
    });

    updateInfo(layers.reverse());
    var t1 = performance.now();
    usedSearch = false;
  }

  function setActive(layer) {
    layer.options.oldColor = layer.options.color;

    if(active) {
      var oldLayer = map._layers[active];
      oldLayer.setStyle({"color": oldLayer.options.oldColor})
    }

    layer.setStyle({"color":"#78a515"});

    active = layer._leaflet_id;
  }

  function getActive() {
    return active;
  }

  function getMap() {
    return map;
  }

  return {
    init: init,
    paintGeoJson: paintGeoJson,
    getMap: getMap,
    getAddress: getAddress,
    data: data,
    addFeature: addFeature,
    updateInfo: updateInfo,
    getLocationsWithinBounds: getLocationsWithinBounds,
    setActive: setActive,
    getActive: getActive,
    monitorAPI: monitorAPI,
    addGroup: addGroup
  };
}();
