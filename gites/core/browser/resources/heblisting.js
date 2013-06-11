'use strict';

jQuery.fn.spin = function (opts) {
    this.each(function () {
        var $this = jQuery(this),
            spinner = $this.data('spinner');

        if (spinner) spinner.stop();
        if (opts !== false) {
            opts = jQuery.extend({
                color: $this.css('color')
            }, opts);
            spinner = new Spinner(opts).spin(this);
            $this.data('spinner', spinner);
        }
    });
    return this;
};

jQuery.fn.serializeObject = function()
{
    var o = {};
    var a = this.serializeArray();
    jQuery.each(a, function() {
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
        $scope.formData = jQuery('#hiddenForm').serializeObject();
        if ( $scope.reference != $scope.formData.reference) {
            $scope.page = 0;
        }
        $scope.reference = $scope.formData.reference;
        var page_cookie = $cookieStore.get('listing_keywords');
        if ( page_cookie ) {
            $scope.keywords = page_cookie;
        }
        $scope.sort = $cookieStore.get('listing_sort', '');
        if ($scope.sort === undefined)
        {
            // XXX Je ne sais pas savoir ici si on est sur une page geolocalized ou pas?
            // ainsi j'ajouterai cette condition avant de prendre 'distance' par defaut
            $scope.sort = "distance";
        }
    };

    var selectedKeywords = function() {
	var selected_keywords = [];
	for (var keyword in $scope.keywords) {
		if ( $scope.keywords[keyword] === true ) {
			selected_keywords.push(keyword);
		};
	};
	return selected_keywords;
    }

    $scope.updatePostData = function() {
        $scope.postData = jQuery.extend($scope.formData, {'keywords': selectedKeywords(),
                                                     'page': $scope.page,
                                                     'sort': $scope.sort,
                                                     'reference': $scope.reference});
    }

    var serializeToHTTPPost = function(data){
        return jQuery.param(data);
    }

    var httpPostconfig = {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
        transformRequest: serializeToHTTPPost
	};

    $scope.updateMap = function() {
        $scope.updatePostData();
        $http.post($scope.map_listing_url, $scope.postData, httpPostconfig).
        success(function(data, status) {
            if (typeof googleMapAPI != 'undefined') {
                googleMapAPI.updateHebergementsMarkers(data);
            }
        })
    };

    $scope.update = function() {
        $scope.updatePostData();
        if ( ! jQuery.isEmptyObject($scope.keywords) ) {
            $cookieStore.put('listing_keywords', $scope.keywords);
        };
        $cookieStore.put('listing_sort', $scope.sort);

        $http.post($scope.listing_url, $scope.postData, httpPostconfig).
        success(function(data, status) {
            $scope.status = status;
            $scope.listcontainer = data;
        });
        $scope.updateMap();
    };

    $scope.compareHeb = function() {
        var comparator_url = '@@hebergement-comparison?heb_pk='
        var comparison_values = [];
        jQuery('input:checked[name="heb-comparison:list"]').each(function() {
            comparison_values.push(jQuery(this).val());
        });

        if(jQuery('#overlay-comparator').length != 0) {
            jQuery('#overlay-comparator').remove();
        }

        jQuery('<div id="overlay-comparator"><div class="contentWrap"></div></div>').appendTo(jQuery('#overlay-container'));

        jQuery('#overlay-comparator').overlay({
            onBeforeLoad: function() {
                this.getOverlay().height('34px');
                var wrap = this.getOverlay().find(".contentWrap");
                wrap.load(comparator_url + comparison_values.join('&heb_pk='));
            },
            onLoad: function() {
                if (this.getOverlay().find('.comparator').height() > 100) {
                    this.getOverlay().height('80%');
                }
            },
        });
        jQuery('#overlay-comparator').overlay().load();
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
        jQuery("#spin").show().spin(opts);
            return data;
        };
        $httpProvider.defaults.transformRequest.push(spinnerFunction);
    })
    .factory('myHttpInterceptor', function ($q, $window) {
        return function (promise) {
            return promise.then(function (response) {
		jQuery("#spin").hide()
                return response;

            }, function (response) {
		jQuery("#spin").hide()
                return $q.reject(response);
            });
        };
    })
