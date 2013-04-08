'use strict';

$.fn.spin = function (opts) {
    this.each(function () {
        var $this = $(this),
            spinner = $this.data('spinner');

        if (spinner) spinner.stop();
        if (opts !== false) {
            opts = $.extend({
                color: $this.css('color')
            }, opts);
            spinner = new Spinner(opts).spin(this);
            $this.data('spinner', spinner);
        }
    });
    return this;
};

var app = angular.module('listing', ['ngSanitize', 'ngCookies']);
app.controller('SearchCtrl', function($scope, $http, $compile, $cookieStore) {

    var init = function() {
        $scope.page = $cookieStore.get('listing_page', 0);
	var baseurl = kukit.engine.baseUrl;
	$scope.listing_url = baseurl + 'update_listing'; // The url of our search
	$scope.map_listing_url = baseurl + 'update_map_listing'; // The url of our search
        $scope.keywords = {};
        var page_cookie = $cookieStore.get('listing_keywords');
	if ( page_cookie ) {
	    $scope.keywords = page_cookie;
	}
	$scope.sort = $cookieStore.get('listing_sort', '');
    };

    // initialize values
    init();

    $scope.updateMap = function() {
        $http.post($scope.map_listing_url, {'keywords': $scope.keywords,
	                        'page': $scope.page,
	                        'sort': $scope.sort}).
        success(function(data, status) {
	    if (typeof googleMapAPI != 'undefined') {
	       googleMapAPI.updateHebergementsMarkers(data);
	    }
        })
    };

    $scope.update = function() {
	if ( $scope.keywords ) {
            $cookieStore.put('listing_keywords', $scope.keywords);
	};
        $cookieStore.put('listing_sort', $scope.sort);
        $http.post($scope.listing_url, {'keywords': $scope.keywords,
	                        'page': $scope.page,
	                        'sort': $scope.sort}).
        success(function(data, status) {
            $scope.status = status;
            $scope.listcontainer = data;
        })
	$scope.updateMap();
    };

    $scope.update();

    $scope.goToNextPage = function(){
	 $scope.page++
	 $scope.goToPage($scope.page);
    }

    $scope.goToPreviousPage = function(){
         $scope.page--;
	 $scope.goToPage($scope.page);
    }


    $scope.goToPage = function(page){
	 $scope.page = page;
         $cookieStore.put('listing_page', page);
	 $scope.update();
    }

    $scope.updateSort = function() {
	 $scope.goToPage(0);
    }

    $scope.updateKeywords = function() {
	 $scope.goToPage(0);
    }

});

app.directive('angularHtmlBind', function($compile) {
    return function(scope, elm, attrs) {
        scope.$watch(attrs.angularHtmlBind, function(newValue, oldValue) {
            if (newValue && newValue !== oldValue) {
                elm.html(newValue);
                $compile(elm.contents())(scope);
            }
        });
    };
});

app.config(function ($httpProvider) {
        $httpProvider.responseInterceptors.push('myHttpInterceptor');
        var spinnerFunction = function (data, headersGetter) {
        var opts = {
            lines: 12, // The number of lines to draw
            length: 7, // The length of each line
            width: 5, // The line thickness
            radius: 10, // The radius of the inner circle
            color: '#fff', // #rbg or #rrggbb
            speed: 1, // Rounds per second
            trail: 66, // Afterglow percentage
            shadow: true // Whether to render a shadow
        };
        $("#spin").show().spin(opts);
            return data;
        };
        $httpProvider.defaults.transformRequest.push(spinnerFunction);
    })
    .factory('myHttpInterceptor', function ($q, $window) {
        return function (promise) {
            return promise.then(function (response) {
		$("#spin").hide()
                return response;

            }, function (response) {
		$("#spin").hide()
                return $q.reject(response);
            });
        };
    })
