module.exports = function() {  
  var map, active = null, usedSearch = false, data = {}, mapboxToken = 'pk.eyJ1Ijoib3VycmV2b2x1dGlvbiIsImEiOiJjaXpzdm91M3UwMDA3MzNvY2NhZXZtZ21hIn0.WBmvgFv12o8eEnv2GsZthA';
    
  function init(mapDiv) {
    initMap(mapDiv);
  }
  
  function initMap(mapDiv) {  
    map = L.map(mapDiv).setView([37.8, -96.9], 4);
    
    var baseLayer = L.tileLayer('https://api.mapbox.com/v4/mapbox.streets/{z}/{x}/{y}.png?access_token=' + mapboxToken, {
        maxZoom: 18 
      }
    ).addTo(map);
    
    $(map).on('zoomend', function() {
      
      // only do this after user has used search box
      if (usedSearch) {
        getLocationsWithinBounds(map.getBounds());
      }  
    });

    $(function(){
      google.maps.event.addDomListener(document.getElementById('autocomplete-input'), 'keydown', function(e) {
        if (e.keyCode === 13 && !e.triggered && $('.pac-item-selected').length == 0) {
          google.maps.event.trigger(this, 'keydown', {
            keyCode: 40
          })
          google.maps.event.trigger(this, 'keydown', {
            keyCode: 13,
            triggered: true
          })
        }
      });
    });
    
    // populate(map);
  }
  
  function getAddress() {
    var geometry, place = autocomplete.getPlace();
    usedSearch = true;

    if (!place.geometry) {
      // TODO: Display this in .app__info
      console.log("We can't find that place - try again.");
      return;
    } else {
      map.flyToBounds([[place.geometry.viewport.getNorthEast().lat(), place.geometry.viewport.getNorthEast().lng()], [place.geometry.viewport.getSouthWest().lat(), place.geometry.viewport.getSouthWest().lng()]]);
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
    var coords = group.geometry.coordinates;
    var marker = L.marker(coords.reverse());
    
    marker.properties = group.properties;
    
    marker.bindPopup('<h4>'+ group.properties.name + '</h1>');
    
    marker.on('click touchstart', function() {
      updateInfo([this]);
    });
    
    marker.addTo(map);
    
  }
  
  function resetInfo() {
    $('.groups-map-info__status').html('');
  }
  
  function updateInfo(groups) {
    var location = '', city, county, state, country;
    
    resetInfo();
        
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
       
      $('.groups-map-info__status').append('\
        <div class="component">\
          <div class="component__heading">\
            <span class="component__location">' + location + '</span>\
            <h4 class="component__name">' + groups[i].properties.name + ((groups[i].properties.state_organizing_committee) ? " (SOC) " : "") + '</h4>\
          </div>\
          <div class="component__info">\
            <a href="/groups/'+ groups[i].properties.slug +'" class="component__cta btn btn-block btn-primary uppercase ls2">Get Involved</a>\
          </div> \
        </div>\
      ');
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
