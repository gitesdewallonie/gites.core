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

var filterValues = function(dict) {
        var selected_values = [];
        for (var key in dict) {
            if ( dict[key] === true ) {
                selected_values.push(key);
            };
        };
        return selected_values;
}


var app = angular.module('listing', ['ngSanitize', 'ngCookies', 'ui.bootstrap']);
app.controller('SearchCtrl', function($scope, $http, $compile) {

    var parseJSON = function(value) {
        return value ? JSON.parse(value) : undefined;
    };

    $scope.init = function() {
        $scope.needUpdate = false;
        var baseurl = calculateBase();
        $scope.listing_url = baseurl + 'update_listing'; // The url of our search
        $scope.map_listing_url = baseurl + 'update_map_listing'; // The url of our search
        var cookieData = jQuery('#hiddenForm').serializeObject();
        $scope.cookieKey = cookieData.cookie_key;
        $scope.parameters = parseJSON(jQuery.cookie($scope.cookieKey));

        if ($scope.parameters === undefined) {
            $scope.parameters = {
                'keywords': {},
                'classifications': {},
                'page': undefined,
                'hash': undefined,
                'sort': jQuery.cookie($scope.cookieKey + '_sort'),
                'data': undefined,
                'hebergementType': {},
                'fromDate': undefined,
                'toDate': undefined,
                'capacity': undefined,
                'nearTo': undefined};
        } else {
            $scope.needUpdate = true;
        }
        $scope.parameters.data = parseJSON(cookieData.request);

        if ( cookieData.hash != $scope.parameters.hash ) {
            $scope.parameters.page = 0;
            $scope.needUpdate = ($scope.parameters.hash === undefined)? false : true;
            $scope.parameters.hash = cookieData.hash;
        }
        $scope.sort = $scope.parameters.sort;
        $scope.keywords = $scope.parameters.keywords;
        $scope.classifications = $scope.parameters.classifications;
        $scope.hebergementType = $scope.parameters.hebergementType;
        $scope.fromDate = $scope.parameters.fromDate;
        $scope.toDate = $scope.parameters.toDate;
        $scope.capacity = $scope.parameters.capacity;
        $scope.nearTo = $scope.parameters.nearTo;
    };

    $scope.updatePostData = function() {
        $scope.postData = jQuery.extend($scope.parameters.data,
                                        {'keywords': filterValues($scope.parameters.keywords),
                                         'page': $scope.parameters.page,
                                         'sort': $scope.parameters.sort,
                                         'reference': $scope.parameters.data.reference,
                                         'form.widgets.fromDateAvancee': $scope.fromDate,
                                         'form.widgets.classification': filterValues($scope.parameters.classifications),
                                         'form.widgets.toDateAvancee': $scope.toDate,
                                         'form.widgets.capacityMin': $scope.capacity,
                                         'form.widgets.nearTo': $scope.nearTo});
        var hebTypes = filterValues($scope.parameters.hebergementType);
        if (hebTypes.length != 0) {
            $scope.postData = jQuery.extend($scope.parameters.data, {'form.widgets.hebergementType': hebTypes});
        }
        else {
            // If no heb type selected, select both
            $scope.postData = jQuery.extend($scope.parameters.data, {'form.widgets.hebergementType': ['gite-meuble', 'chambre-hote']});
        }
    }

    var serializeToHTTPPost = function(data){
        return jQuery.param(data);
    }

    var httpPostconfig = {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
        transformRequest: serializeToHTTPPost
    };

    $scope.updateMap = function() {
        $scope.spin();
        $scope.updatePostData();
        $http.post($scope.map_listing_url, $scope.postData, httpPostconfig).
        success(function(data, status) {
            if (typeof googleMapAPI != 'undefined') {
                googleMapAPI.updateHebergementsMarkers(data);
                giteMapHandlers.initExternalDigitMarkerHandlers();
            }
        });
    };

    $scope.update = function() {
        if ($scope.needUpdate === true) {
            $scope.spin();
            $scope.updatePostData();
            jQuery.cookie($scope.cookieKey, JSON.stringify($scope.parameters), {path: '/'});

            $http.post($scope.listing_url, $scope.postData, httpPostconfig).
            success(function(data, status) {
                $scope.status = status;
                $scope.listcontainer = data;
            });
        }
        if (jQuery('#viewlet-map').length) {
            $scope.updateMap();
        }
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
                var overlay = this.getOverlay();
                var wrap = overlay.find('.contentWrap');
                wrap.hide();
                overlay.height('34px');
                wrap.load(comparator_url + comparison_values.join('&heb_pk='), function() {
                    var overlay = jQuery('#overlay-comparator');
                    overlay.find('.spinner').hide();
                    overlay.find('.contentWrap').show();
                    if(overlay.find('.comparator').height() > 100) {
                        overlay.height('80%');
                    }
                });
                // Adds the spinner
                var opts = {
                    lines: 10, // The number of lines to draw
                    length: 6, // The length of each line
                    width: 4, // The line thickness
                    radius: 6, // The radius of the inner circle
                    color: '#999', // #rbg or #rrggbb
                    speed: 1, // Rounds per second
                    trail: 66, // Afterglow percentage
                    shadow: false, // Whether to render a shadow
                    top: '5',
                    left: '477',
                };
                overlay.spin(opts);
            },
        });
        jQuery('#overlay-comparator').overlay().load();
    };

    $scope.goToNextPage = function(){
        $scope.parameters.page++
        $scope.goToPage($scope.parameters.page);
    }

    $scope.goToPreviousPage = function(){
        $scope.parameters.page--;
        $scope.goToPage($scope.parameters.page);
    }


    $scope.goToPage = function(page){
        $scope.needUpdate = true;
        $scope.parameters.page = page;
        jQuery.cookie($scope.cookieKey, JSON.stringify($scope.parameters), {path: '/'});
        $scope.update();
    }

    $scope.updateSort = function() {
        $scope.parameters.sort = $scope.sort;
        $scope.goToPage(0);
    }

    $scope.updateKeywords = function() {
        $scope.goToPage(0);
    }

    $scope.spin = function () {
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
    };


    // initialize values
    $scope.init();

    $scope.update();
});

app.controller(
        "collapseCtrl",
        function($scope, $http, $compile){
            $scope.isCollapsed = false;
            $scope.data = null;
            $scope.getGroupement = function(pk) {
                jQuery(".collapse-gite-listing-detail").show();
                jQuery(".collapse-chambre-listing-detail").show();
                if ($scope.isCollapsed == false){
                $http({
                        url: "getGroupementByPk",
                        method: "POST",
                        data: "pk="+parseInt(pk),
                        headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                }).success(function(data, status, headers, config) {
                        $scope.data = data;
                        $scope.status = status;
                        $scope.isCollapsed = true;
                }).error(function(data, status, headers, config) {
                        $scope.status = status;
                });
                }
                else {
                    $scope.isCollapsed = false;
                }
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

app.factory('myHttpInterceptor', function ($q, $window) {
    return function (promise) {
        return promise.then(function (response) {
            jQuery("#spin").hide();
            return response;
        }, function (response) {
            jQuery("#spin").hide();
            return $q.reject(response);
        });
    };
});

app.config(function ($httpProvider) {
    $httpProvider.responseInterceptors.push('myHttpInterceptor');
});

app.directive('datepick', function() {
    return {
        restrict: 'A',
        require : 'ngModel',
        link : function (scope, element, attrs, ngModelCtrl) {
            $(function(){
                jQuery(element).datepicker({
                    minDate: 0,
                    dateFormat:'dd/mm/yy',
                    buttonImage: "++theme++gites.theme/images/icon_calendrier.png",
                    buttonImageOnly: true,
                    showOn: "both",
                    onSelect:function (date) {
                        ngModelCtrl.$setViewValue(date);
                        scope.$apply();
                        scope.updateKeywords();
                    }
                });
            });
        }
    }
});
