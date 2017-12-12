CanvasJS.addCultureInfo("de",
                {
                    days: ["Sonntag", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag"],
                    shortDays: ["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa"],
                    months: ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"],
                    shortMonths: ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
               });

function loadData(value, dingroup, dateStart, dateEnd, type){
  $.ajax({
    url: "/api/analogValues",
    contentType: "application/json",
    type: "get", //send it through get method
    data: {
      value: value,
      dingroup: dingroup,
      dateStart: dateStart,
      dateEnd: dateEnd
    },
    success: function(response) {
      var data = [];
      var dataSeries = { type: type };

      dataSeries.dataPoints = response.map((entry) => {
        entry.x = new Date(entry.x);
        return entry;
      });

      data.push(dataSeries);
      console.log(data);
      drawChart(data);
    },
    error: function(err) {
      console.log("Error" + err);
    }
  });
}

function drawChart(data){
  var chart = new CanvasJS.Chart("chart1", {
    culture:  "de",
  	animationEnabled: true,
  	zoomEnabled: true,
    zoomType: "xy",
  	data: data
  });
  chart.render();
}

function drawPieChart(){
  var chart = new CanvasJS.Chart("chart2",
	{
		legend: {
			maxWidth: 350,
			itemWidth: 120
		},
		data: [
		{
			type: "pie",
			showInLegend: true,
			legendText: "{indexLabel}",
			dataPoints: [
				{ y: 145553, indexLabel: "DinGroup 34" },
				{ y: 1467952, indexLabel: "DinGroup 35" },
				{ y: 2881345, indexLabel: "DinGroup 36" },
				{ y: 9855, indexLabel: "DinGroup 37" },
				{ y: 218268, indexLabel: "DinGroup 38" },
				{ y: 1059028, indexLabel: "DinGroup 39" },
				{ y: 1097817, indexLabel: "DinGroup 40" },
				{ y: 49126, indexLabel: "DinGroup 41" },
				{ y: 3722, indexLabel: "DinGroup 42" },
				{ y: 23716, indexLabel: "DinGroup 43" },
				{ y: 9395, indexLabel: "DinGroup 44" },
				{ y: 811166, indexLabel: "DinGroup 2034" },
				{ y: 282138, indexLabel: "DinGroup 2035" },
				{ y: 572312, indexLabel: "DinGroup 2036" },
				{ y: 2141, indexLabel: "DinGroup 2037" },
				{ y: 38304, indexLabel: "DinGroup 2038" },
				{ y: 210181, indexLabel: "DinGroup 2039" },
				{ y: 9631, indexLabel: "DinGroup 2040" },
				{ y: 578, indexLabel: "DinGroup 2041" },
				{ y: 4627, indexLabel: "DinGroup 2042" },
				{ y: 2128, indexLabel: "DinGroup 2043" },
				{ y: 504262, indexLabel: "DinGroup 2044" },
				{ y: 710531, indexLabel: "DinGroup 2045" },
				{ y: 229, indexLabel: "DinGroup 2046" }
			]
		}
		]
	});
	chart.render();
}

function showLoadingView(){
  $("#chart1").empty();
  $("#chart1").append('<img id="loadingImage" src="images/loading_train.gif"/>');
  $("#loadingImage").css("visibility", "visible");
}

$( document ).ready(function() {
  drawPieChart();
  $('.input-daterange').datepicker({
    format: 'dd.mm.yyyy'
  });

  $( "#buttonShow" ).click(function() {
    showLoadingView();
    loadData(parseInt($("#inputValue").val()), parseInt($("#inputDingroup").val()), $("#dateStart").val(), $("#dateEnd").val(), $("#inputVisualize").val())
  });
});
