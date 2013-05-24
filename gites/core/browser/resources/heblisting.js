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

$.fn.serializeObject = function()
{
    var o = {};
    var a = this.serializeArray();
    $.each(a, function() {
        if (o[this.name] !== undefined) {
            if (!o[this.name].push) {
                o[this.name] = [o[this.name]];
            }
            o[this.name].push(this.value || '');
        } else {
            o[this.name] = this.value || '';
        }
    });
    return o;
};

// Calculate base href - code coming from kss

var calculateBaseOnInstance = function(documentInstance, pageLocation) {
    var base = '';
    var nodes = documentInstance.getElementsByTagName("link");
    if (nodes.length > 0) {
        for (var i=0; i<nodes.length; i++) {
            var link = nodes[i];
            if ((link.rel == 'kss-base-url')||(link.rel == 'alternate' && link.getAttribute('data-kss-base-url') != null)) {
                var base = link.href;
                if (! /\/$/.test(base)) {
                    base = base + '/';
                }
            }
        }
    }
    if (!base) {
        nodes = documentInstance.getElementsByTagName("base");
        if (nodes.length != 0) {
            var base = nodes[0].href;
        } else {
            var base = pageLocation;
        }
    }
    var pieces = base.split('/');
    pieces.pop();
    base = pieces.join('/') + '/';
    return base;
};


var calculateBase = function() {
    var base = '';
    // returns empty base when not in browser (cli tests)
    try {
        var _dummy = document;
        _dummy = window;
    } catch (e) {
        // testing or what
        return base;
    }
    base = calculateBaseOnInstance(document, window.location.href);
    return base;
};

var app = angular.module('listing', ['ngSanitize', 'ngCookies']);
app.controller('SearchCtrl', function($scope, $http, $compile, $cookieStore) {

    $scope.init = function() {
        $scope.page = $cookieStore.get('listing_page', 0);
        var baseurl = calculateBase();
        $scope.listing_url = baseurl + 'update_listing'; // The url of our search
        $scope.map_listing_url = baseurl + 'update_map_listing'; // The url of our search
        $scope.keywords = {};
        $scope.formData = $('#hiddenForm').serializeObject();
        if ( $scope.reference != $scope.formData.reference) {
            $scope.page = 0;
        }
        $scope.reference = $scope.formData.reference;
        var page_cookie = $cookieStore.get('listing_keywords');
        if ( page_cookie ) {
            $scope.keywords = page_cookie;
        }
        $scope.sort = $cookieStore.get('listing_sort', '');
    };

    $scope.updatePostData = function() {
        $scope.postData = $.extend($scope.formData, {'keywords': $scope.keywords,
                                                     'page': $scope.page,
                                                     'sort': $scope.sort,
                                                     'reference': $scope.reference});
    }

    $scope.updateMap = function() {
        $scope.updatePostData();
        $http.post($scope.map_listing_url, $scope.postData).
        success(function(data, status) {
            if (typeof googleMapAPI != 'undefined') {
                googleMapAPI.updateHebergementsMarkers(data);
            }
        })
    };

    $scope.update = function() {
        $scope.updatePostData();
        if ( ! $.isEmptyObject($scope.keywords) ) {
            $cookieStore.put('listing_keywords', $scope.keywords);
        };
        $cookieStore.put('listing_sort', $scope.sort);

        $http.post($scope.listing_url, $scope.postData).
        success(function(data, status) {
            $scope.status = status;
            $scope.listcontainer = data;
        })
        $scope.updateMap();
    };


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

    // initialize values
    $scope.init();

    $scope.update();
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


jQuery('div#listing-result-block').ready(function($) {

  $('input#comparison-button').click(function() {
    alert('bla');
  });

});
