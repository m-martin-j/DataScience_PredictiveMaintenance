function loadData(value, dingroup, dateStart, dateEnd){
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
      var dataSeries = { type: "column" };
      response = response.map((entry) => {
        entry.x = new Date(entry.x);
        return entry;
      });
      dataSeries.dataPoints = response;
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
  	animationEnabled: true,
  	zoomEnabled: true,
  	axisY :{
  		includeZero:true
  	},
  	data: data
  });
  chart.render();
}

$( document ).ready(function() {
  $('.input-daterange').datepicker({
    format: 'dd.mm.yyyy'
  });

  $( "#buttonShow" ).click(function() {
    loadData(parseInt($("#inputValue").val()), parseInt($("#inputDingroup").val()), $("#dateStart").val(), $("#dateEnd").val())
  });
});
