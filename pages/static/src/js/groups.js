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
    })
    
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
      geometry = [place.geometry.location.lat(),place.geometry.location.lng()]; 
      positionMap(geometry);
    }
  }
  
  function positionMap(geometry) {       
    map.flyTo(geometry, 12, {duration:1});
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
  
  function addMarker(point, popupHTML, tooltipHTML) {
    var marker = L.marker(point);
    
    if (popupHTML) {
      marker.bindPopup(popupHTML);
    }
    
    if (tooltipHTML) {
      marker.bindTooltip(tooltipHTML);
    }
    
    marker.on('click touchstart', function(e) {
      console.log(this);
    });
    
    marker.addTo(map);
  }
  
  function addGroup(group) {
    console.log(group);
    
    addMarker(group.)
  }
  
  function resetInfo() {
    $('.app-info__status').html('');
  }
  
  function updateInfo(layers) {
    resetInfo();
    
    for (var i=0; i<layers.length; i++) {
    
      var description, name = "";
      
      if(layers[i].properties.model == "map.county") {
        name = layers[i].properties.name;
        
        if (!layers[i].properties.jails_honor_ice_detainers_short_answer.includes('N/A')) {
          description = layers[i].properties.jails_honor_ice_detainers_short_answer;
        }
      } else {
        name = layers[i].properties.name;
        
        if (!layers[i].properties.limited_ice_cooperation_short_answer.includes('N/A')) {
          description = layers[i].properties.limited_ice_cooperation_short_answer;
        }
      }
      
      if (!description) {
        description = "Click the button below to learn more about " + layers[i].properties.name + "'s policies and how you can get involved."
      }
                
      layers[i].options.oldColor = layers[i].options.color;
      
      $('.app-info__status').prepend('\
        <div class="component">\
          <div class="component__heading">\
            <h4 class="component__name">' + name + '</h4>\
          </div>\
          <div class="component__info">\
            <p class="component__description">\
              ' + description + '\
            </p>\
            <a href="/'+ layers[i].properties.slug +'" class="component__cta btn btn-block btn-primary">Learn More & Get Involved</a>\
          </div> \
        </div>\
      ');
      
    }
    
  }
  
  function getLocationsWithinBounds(bounds) {
    var layers = [], t0 = performance.now();
    
    map.eachLayer(function (layer) {
      if(layer.properties) {
        layer.eachLayer(function (sublayer) {              
          if(bounds.intersects(sublayer.getBounds())) {
            layers.push(layer);
          }
        })
      }
      
    });
    
    updateInfo(layers);
    var t1 = performance.now();
    console.log("Call took " + (t1 - t0) + " milliseconds.")
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
    addMarker: addMarker,
    addGroup: addGroup
  };   
}();
