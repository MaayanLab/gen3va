function createAndManageVisualizations(config) {

    var clustergrams = [];

    $(function() {
        var elem;
        dataTables();
        watchClustergramWidths();
        plotPCA(config.pcaPlot);
        try {
            elem = '#genes-heat-map';
            createClustergram(
                elem,
                config.genesHeatMap
            );
        } catch (e) {
            $(elem).hide();
            console.log(e);
        }
        try {
            elem = '#l1000cds2-heat-map';
            createClustergram(
                elem,
                config.l1000cds2HeatMap
            );
        } catch (e) {
            $(elem).hide();
            console.log(e);
        }
        try {
            elem = '#enrichr-heat-maps';
            createAndWatchEnrichrHeatMaps(elem, config.enrichrHeatMaps);
        } catch (e) {
            $(elem).hide();
            console.log(e);
        }
    });

    function createAndWatchEnrichrHeatMaps(elem, enrichrHeatMaps) {
        var $enrichr = $(elem),
            len = length(enrichrHeatMaps),
            heatMap,
            rootElement,
            i;

        for (i = 0; i < len; i++) {
            heatMap = enrichrHeatMaps[i];
            rootElement = '#' + heatMap.enrichr_library;
            $enrichr.append(
                '<div ' +
                '   id="' + heatMap.enrichr_library + '"' +
                '   class="heat-map enrichr-heat-map"' +
                '></div>'
            );
            createClustergram(rootElement, heatMap);
        }

        showEnrichrHeatMap(enrichrHeatMaps[0].enrichr_library);
        watchEnrichrClustergram($enrichr, enrichrHeatMaps);
    }

    function createClustergram(rootElement, clustergramData) {
        var clustergram = Clustergrammer({
            root: rootElement,
            // This specifies the filtering for the clustergram.
            // For more, see:
            // https://github.com/MaayanLab/clustergrammer.js/blob/master/load_clustergram.js
            ini_view: {N_row_sum :50},
            network_data: clustergramData.network
        });
        try {
            makeClustergramColorLegend(rootElement, clustergram.params.viz.cat_colors.col['cat-0']);
            moveClustergramControls(rootElement);
        } catch (e) {
            console.log(e);
        }
        try {
            filterClustergramColsOnClick(clustergram);
        } catch (e) {
            console.log(e);
        }
        clustergrams.push(clustergram);
    }

    function filterClustergramColsOnClick(clustergram) {
        // These variables are used to disambiguate a single click from a
        // double click. See: http://stackoverflow.com/a/7845282
        var DELAY = 500,
            clicks = 0,
            timer = null;
        $(clustergram.config.root).find('.col_label_group text')
            .click(function(evt) {
                var $this = $(this);
                clicks++;
                if (clicks === 1) {
                    timer = setTimeout(function() {
                        clicks = 0;
                        var colToHide = $this.attr('full_name');
                        hideColumn(clustergram, colToHide);
                        hideD3Tooltip(colToHide);
                        createClustergramResetButton(clustergram);
                    }, DELAY);
                } else {
                    clearTimeout(timer);
                    clicks = 0;
                }

            })
            .dblclick(function(evt) {
                evt.preventDefault();
            });
    }

    function hideColumn(clustergram, colToHide) {
        var allCols = clustergram.config.network_data.col_nodes_names,
            colsToKeep = remove(allCols, colToHide);
        clustergram.filter_viz_using_names({'col': colsToKeep});
    }

    // This is a hacky method. When you filter a clustergram, the tooltip does
    // not disappear. Normally, I would ask Nick to fix this in Clustergrammer,
    // but I need this wrapped up today.
    function hideD3Tooltip(colToHide) {
        $('.d3-tip span:contains("' + colToHide + '")').parent().css({opacity: 0});
    }

    function createClustergramResetButton(clustergram) {
        if ($(clustergram.config.root).find('.reset-button').length) {
            return;
        }
        var $button = $('<button class="btn btn-info reset-button">Reset heatmap</button>');
        $(clustergram.config.root).find('.color-legend').after($button);
        $button.click(function() {
            // This resets the clustergram according to an email from Nick.
            clustergram.update_view({'n_row_sum':'all'});
            $button.remove();
        });
    }

    function makeClustergramColorLegend(rootElement, colors) {
        var list = '',
            isHidden = true,
            MAX_CATS_BEFORE_HIDE = 20,
            $legend,
            $ul,
            $h3;
        $.each(colors, function(categoryName, hex) {
            categoryName = $.trim(categoryName.split(':')[1]);
            var rgb = hexToRgb(hex),
                rgba = 'rgba(' + rgb.r + ',' + rgb.g + ',' + rgb.b + ',.6)';
            list += '' +
                '<li style="border-left: 13px solid ' + rgba + '";>' +
                    categoryName +
                '</li>';
        });
        $legend = $(
            '<div class="color-legend">' +
                '<h3 class="btn btn-info">Show color legend</h3>' +
                '<ul class="list-inline">' +
                    list +
                '</ul>' +
                '<div class="clear"></div>' +
            '</div>'
        );
        $ul = $legend.find('ul');
        $h3 = $legend.find('h3');
        $(rootElement).prepend($legend);
        if (length(colors) > MAX_CATS_BEFORE_HIDE) {
            $ul.hide();
            $h3.click(function(evt) {
                if (isHidden) {
                    isHidden = false;
                    $ul.show();
                    $h3.text('Hide color legend');
                } else {
                    isHidden = true;
                    $ul.hide();
                    $h3.text('Show color legend');
                }
            });
        } else {
            $h3.hide();
        }
    }

    // Clustergrammer controls have 15px left padding. We want to remove this
    // so the controls line up with the left-hand side of the page. We use
    // jQuery because we need to override inline styling.
    function moveClustergramControls(rootElement) {
        $(rootElement).find(
            '.title_section,' +
            '.about_section,' +
            '.icons_section,' +
            '.reorder_section,' +
            '.gene_search_container,' +
            '.opacity_slider_container,' +
            '.dendro_sliders,' +
            '.div_filters'
        ).css({
            'padding-left': 0
        });
        // Prevent slider from going outside the div, i.e. disappearing halfway.
        $('.d3-slider-handle').css({
            'margin-left': 0,
            width: '.5em'
        });
    }

    function watchEnrichrClustergram($enrichr, enrichrHeatMaps) {
        // When the user selects a new library, toggle the visible library.
        $enrichr.find('select').change(function(evt) {
            var newEnrichrLibrary = $(evt.target).val();
            showEnrichrHeatMap(newEnrichrLibrary);
        });
    }

    function showEnrichrHeatMap(enrichrLibrary) {
        $('.enrichr-heat-map').hide();
        $('#' + enrichrLibrary).show();
    }

    function dataTables() {
        $('table').DataTable({ iDisplayLength: 5 });
    }

    function watchClustergramWidths() {
        // Debounce this resizing callback because it's fairly intensive.
        $(window).resize(_.debounce(function() {
            $.each(clustergrams, function(i, clustergram) {
                clustergram.resize_viz();
            });
        }, 250));
    }

    function plotPCA(pcaObj) {
        if (typeof pcaObj === 'undefined')
            return;

        // If there is only one data series, use Geneva's blue. Otherwise,
        // let Highcharts figure it out.
        if (pcaObj.series.length == 1) {
            Highcharts.setOptions({
                colors: ['#1689E5']
            });
        }

        var tooltipFormatter = function() { return this.key; },
            mins = pcaObj.ranges[1],
            maxs = pcaObj.ranges[0],
            titles = pcaObj.titles,
            chart;

        chart = new Highcharts.Chart({
            chart: {
                renderTo: 'pca-plot',
                margin: [150, 150, 150, 150],
                type: 'scatter',
                options3d: {
                    enabled: true,
                    alpha: 20,
                    beta: 30,
                    depth: 500
                }
            },
            legend: {
                floating: true,
                layout: 'vertical',
                align: 'left',
                verticalAlign: 'top'
            },
            title: {
                text: '3D PCA plot'
            },
            subtitle: {
                text: 'using x y z coordinates'
            },
            xAxis: {
                title: {text: titles[0]},
                min: mins[0],
                max: maxs[0]
            },
            yAxis: {
                title: {text: titles[1]},
                min: mins[1],
                max: maxs[1]
            },
            zAxis: {
                title: {text: titles[2]},
                min: mins[2],
                max: maxs[2]
            },
            series: pcaObj.series,
            tooltip: {
                formatter: tooltipFormatter,
                useHTML: true,
                backgroundColor: '#7FB800', // green
                borderColor: '#7FB800',
                borderRadius: 0,
                shadow: false,
                style: {
                    color: 'white',
                    fontFamily: 'Roboto',
                    fontWeight: 'bold',
                    padding: 6
                }
            }
        });

        // Add mouse events for rotation
        $(chart.container).bind('mousedown.hc touchstart.hc', function (e) {
            e = chart.pointer.normalize(e);

            var posX = e.pageX,
                posY = e.pageY,
                alpha = chart.options.chart.options3d.alpha,
                beta = chart.options.chart.options3d.beta,
                newAlpha,
                newBeta,
                sensitivity = 5; // lower is more sensitive

            $(document).bind({
                'mousemove.hc touchdrag.hc': function (e) {
                    newBeta = beta + (posX - e.pageX) / sensitivity;
                    chart.options.chart.options3d.beta = newBeta;
                    newAlpha = alpha + (e.pageY - posY) / sensitivity;
                    chart.options.chart.options3d.alpha = newAlpha;
                    chart.redraw(false);
                },
                'mouseup touchend': function () {
                    $(document).unbind('.hc');
                }
            });
        });
    }


    // Utility function from:
    // http://stackoverflow.com/a/3954451
    function remove(array, item) {
        var index = array.indexOf(item);
        array.splice(index, 1);
        return array
    }

    function length(obj) {
        var size = 0, key;
        for (key in obj) {
            if (obj.hasOwnProperty(key)) size++;
        }
        return size;
    }

    function hexToRgb(hex) {
        var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : null;
    }

    // For debugging.
    window.clustergrams = clustergrams;
}