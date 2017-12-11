google.charts.load('current', {'packages':['line']});
google.charts.setOnLoadCallback(loadData);

function loadData(){
  $.ajax({
    url: "/api/analogValues",
    contentType: "application/json",
    type: "get", //send it through get method
    data: {
      value: 2,
      dingroup: 2034
    },
    success: function(response) {      
      drawChart(response);
    },
    error: function(err) {
      console.log("Error" + err);
    }
  });
}

function drawChart(values) {
  var data = new google.visualization.DataTable();
  data.addColumn('number', 'Date');
  data.addColumn('number', 'Value');

  data.addRows(values);

  var options = {
    chart: {
      title: 'Box Office Earnings in First Two Weeks of Opening',
      subtitle: 'in millions of dollars (USD)'
    },
    width: 900,
    height: 500
  };

  var chart = new google.charts.Line(document.getElementById('chart1'));

  console.log("drawing chart");
  chart.draw(data, google.charts.Line.convertOptions(options));
}
