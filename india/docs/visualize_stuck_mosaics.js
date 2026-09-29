// Visualizacao dos mosaicos TRAVADOS (RUNNING >= 6h)
// (71 celulas-anos, 40 celulas unicas — ver docs/stuck_mosaics_report.md)

var GRID = "projects/mapbiomas-india/assets/mosaic_v2_inputs/grid";
var COLLECTION = "projects/mapbiomas-mosaics/assets/LANDSAT/LULC/INDIA/mosaics-2";

var STUCK_CELLS = ["NF-45-X-D", "NG-42-X-B", "NG-42-X-C", "NG-42-Z-A", "NG-43-V-B", "NG-43-V-C", "NG-43-V-D", "NG-43-X-A", "NG-43-X-C", "NG-43-X-D", "NG-45-V-A", "NG-45-V-C", "NG-45-Y-B", "NG-45-Y-C", "NG-45-Y-D", "NG-46-X-B", "NG-46-Z-D", "NH-42-Z-D", "NH-43-X-A", "NH-43-Y-C", "NH-43-Y-D", "NH-44-V-A", "NH-44-V-B", "NH-44-V-C", "NH-44-Y-B", "NH-45-Z-C", "NH-46-Z-A", "NH-46-Z-C", "NH-46-Z-D", "NI-43-V-A", "NI-43-Y-B", "NI-43-Y-D", "NI-43-Z-A", "NI-43-Z-C", "NI-43-Z-D", "NI-44-Y-C", "NI-44-Y-D", "NJ-43-Y-C", "NJ-43-Z-A", "NJ-43-Z-D"];
var STUCK_CELL_YEARS = ["NI_44_Y_C_2021", "NG_43_V_B_2022", "NI_43_Z_D_2021", "NG_45_Y_C_2024", "NI_43_Z_C_2021", "NG_45_Y_D_2024", "NG_43_X_C_2021", "NG_45_Y_C_2023", "NI_44_Y_D_2022", "NI_44_Y_D_2015", "NJ_43_Z_A_2023", "NI_44_Y_D_2025", "NI_44_Y_D_2020", "NI_44_Y_D_2019", "NI_44_Y_C_2024", "NI_43_Z_C_2017", "NI_44_Y_D_2017", "NI_44_Y_D_2016", "NI_43_Z_D_2022", "NI_43_Z_D_2017", "NI_43_Y_D_2017", "NI_44_Y_C_2017", "NG_43_V_C_2019", "NI_44_Y_C_2016", "NI_43_Y_B_2021", "NH_44_V_B_2021", "NG_42_X_C_2019", "NI_44_Y_C_2020", "NG_45_Y_D_2021", "NG_43_V_D_2016", "NG_43_V_D_2019", "NI_43_Z_D_2016", "NI_43_Z_C_2016", "NI_43_Y_D_2016", "NJ_43_Z_D_2021", "NI_43_Z_D_2019", "NG_43_X_D_2017", "NI_44_Y_D_2014", "NG_42_X_B_2015", "NI_43_Z_D_2025", "NH_44_V_A_2021", "NI_43_Z_C_2020", "NG_43_X_A_2019", "NJ_43_Z_A_2020", "NG_45_V_A_2022", "NG_46_Z_D_2020", "NI_43_Z_D_2008", "NH_43_Y_D_2017", "NH_43_Y_C_2013", "NG_42_Z_A_2019", "NG_45_V_A_2020", "NH_46_Z_A_2008", "NH_46_Z_C_2018", "NG_45_V_C_2005", "NI_43_V_A_2010", "NH_46_Z_D_2018", "NH_45_Z_C_2005", "NG_45_Y_B_1992", "NJ_43_Y_C_2012", "NG_46_X_B_2000", "NG_45_Y_B_1989", "NH_43_X_A_1994", "NG_45_Y_C_2000", "NH_44_Y_B_2012", "NH_42_Z_D_1993", "NF_45_X_D_1992", "NI_43_Z_A_2002", "NI_43_V_A_1995", "NF_45_X_D_1988", "NH_44_V_C_2001", "NH_44_V_B_1991"];

var grid = ee.FeatureCollection(GRID);
Map.addLayer(grid.style({color: "666666", width: 1, fillColor: "00000000"}),
             {}, "Grade (283 celulas)", false);

var stuck = grid.filter(ee.Filter.inList("name", STUCK_CELLS));
Map.addLayer(stuck.style({color: "FF0000", width: 2, fillColor: "FF000033"}),
             {}, "Celulas travadas (" + STUCK_CELLS.length + ")", true);

var label = ui.Label("Mosaicos travados");
var select = ui.Select({
  items: STUCK_CELL_YEARS.sort(),
  placeholder: "Escolha celula-ano",
  style: {stretch: "horizontal"}
});

var vis = {bands: ["red_median", "green_median", "blue_median"],
            min: 0, max: 4000, gamma: 1.3};
var LAYER_NAME = "__mosaico__";

function show(name) {
  Map.layers().forEach(function(l) {
    if (l.getName() === LAYER_NAME) { Map.remove(l); }
  });
  var cell = name.split("_").slice(0, 4).join("-");
  Map.addLayer(ee.Image(COLLECTION + "/" + name), vis, LAYER_NAME);
  var g = ee.FeatureCollection(GRID).filter(ee.Filter.eq("name", cell)).geometry();
  Map.centerObject(g, 8);
}

select.onChange(show);
var panel = ui.Panel([label, select], ui.Panel.Layout.flow("vertical"));
Map.add(panel);
Map.setCenter(84, 22, 5);

print("Celulas travadas:", STUCK_CELLS.length);
print("Celulas-anos travadas:", STUCK_CELL_YEARS.length);
