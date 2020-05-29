/**
 * http://usejsdoc.org/
 */
function point2LatLng(point, map) {
        var topRight = map.getProjection().fromLatLngToPoint(map.getBounds().getNorthEast());
        var bottomLeft = map.getProjection().fromLatLngToPoint(map.getBounds().getSouthWest());
        var scale = Math.pow(2, map.getZoom());
        var worldPoint = new google.maps.Point(point.x / scale + bottomLeft.x, point.y / scale + topRight.y);
        return map.getProjection().fromPointToLatLng(worldPoint);
}

var convertedPointsMain = [];

for (var i = 0; i < pxlMainPolygons[p].length; i++) {
    var conv_point = {
        x: Math.round(pxlMainPolygons[p][i][1]),
        y: Math.round(pxlMainPolygons[p][i][0])
    }; 
    convertedPointsMain[i] = point2LatLng(conv_point, map);
}

console.log(convertedPointsMain);