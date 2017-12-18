var initalTableHtml;

function loadData(){
  $.ajax({
    url: "/api/warnings",
    contentType: "application/json",
    type: "get", //send it through get method
    data: {
      dateStart: $("#dateStart").val(),
      dateEnd: $("#dateEnd").val(),
      includeInfos: $("#checkboxInfos").parent().hasClass('checked'),
      includeWarnings: $("#checkboxWarnings").parent().hasClass('checked'),
      includeErrors: $("#checkboxAlarms").parent().hasClass('checked')
    },
    success: function(response) {
      createTable(response);
    },
    error: function(err) {
      console.log("Error" + err);
    }
  });
}

function formateDate(millis){
  var d = new Date(millis);
  return ("0" + d.getDate()).slice(-2) + "." + ("0"+(d.getMonth()+1)).slice(-2) + "." +
    d.getFullYear() + " " + ("0" + d.getHours()).slice(-2) + ":" + ("0" + d.getMinutes()).slice(-2) + " Uhr";
}

function createTable(data){
  $("#tableContainer").empty();
  $("#tableContainer").html(initalTableHtml);

  data.forEach((entry) => {
    var label = "label-warning";
    if (entry[1] == "Alarm"){
      label = "label-danger";
    }else if (entry[1] == "Hinweis"){
      label = "label-primary";
    }
    $('#warningTable > tbody').append('<tr><td>' + formateDate(entry[0]) + '</td><td><span class="label ' + label + '">' + entry[1] + '</span></td><td>' + entry[2] + '</td></tr>');
  });

  $('#warningTable').DataTable({
    "language": {
      "paginate": {
        "next": "Nächste Seite",
        "previous": "Vorherige Seite"
      },
      "lengthMenu": "_MENU_ Einträge pro Seite",
      "info":       "Zeige _START_ bis _END_ von _TOTAL_ Einträgen",
      "search":      "Suche:",
      "zeroRecords":  "Keine passenden Einträge gefunden",
      "infoEmpty":      "Zeige 0 Einträge",
      "infoFiltered":   "(gefiltert aus _MAX_ Einträgen)",
      "thousands":      "."
    },
    "initComplete": $("#imageContainer").remove()
  });
}

$( document ).ready(function() {
  initalTableHtml = $("#tableContainer").html();
  $("#tableContainer").empty();

  $("#buttonShow").click(() => {
    $("#tableContainer").empty();
    $("#tableContainer").parent().append('<div id="imageContainer"><div id="loadingImageWarnings"></div></div>');
    loadData();
  });

  $(".checkbox").each(function() {
    $(this).iCheck({
      checkboxClass: 'icheckbox_line-blue',
      insert: '<div class="icheck_line-icon"></div>' + $(this).attr("text")
    });
  });

  $('.input-daterange').datepicker({
    format: 'dd.mm.yyyy'
  });
});
