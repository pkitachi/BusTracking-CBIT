$(document).ready(function () {
  function show_error(errorobj) {
    $("#error-msg").text(errorobj.error);
    $("#error-msg").css({ visibility: "visible" });
    $("#error-msg").slideDown(function () {
      setTimeout(function () {
        $("#error-msg").slideUp();
      }, 1000);
    });

    $("#example").css({ visibility: "hidden" });
  }

  $("#error-msg").css({ visibility: "hidden" });
  $("#example").css({ visibility: "hidden" });
  $.fn.dataTable.ext.errMode = "throw";

  var url = "http://localhost:5000/api/alerts";
  $("#example").dataTable().fnDestroy();

  $(function () {
    $("#start_date").datetimepicker({
      dateFormat: "dd-mm-yy",
      maxDate: $.now(),
      useCurrent: false,
      format: "L",
    });
  });
  $(function () {
    $("#end_date").datetimepicker({
      dateFormat: "dd-mm-yy",
      maxDate: $.now(),
      useCurrent: false,
      format: "L",
    });
  });
  function preformatdate(date) {
    newdate = date.split("/");
    newdate = newdate[2] + "-" + newdate[0] + "-" + newdate[1];
    return newdate;
  }
  function getDataFromApi(start, end, routeId) {
    let config = {
      headers: {
        Authorization:
          "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1ODkxNzIyOTUsIm5iZiI6MTU4OTE3MjI5NSwianRpIjoiOTJjMGQ1MWUtMGI1NC00OTIwLTlhMWQtN2I1MTk3M2ZkODQ3IiwiaWRlbnRpdHkiOjIsImZyZXNoIjpmYWxzZSwidHlwZSI6ImFjY2VzcyJ9.51ZMsgFF61frmYOTijjmyg_bsVkF3DId6pU9LbAsCQ8",
      },
      params: {
        routeId: routeId,
        fromDate: start,
        toDate: end,
      },
    };
    axios
      .get(
        "http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/reports/fleet",
        config
      )
      .then((response) => {
        console.log(response.data);
        show_data_table(response.data);
      })
      .catch(function (error) {
        console.log(error);
      });
  }

  //  datatable function
  function show_data_table(results) {
    $("#example").css({ visibility: "visible" });
    $("#example").DataTable({
      responsive: true,
      data: results,
      columns: [
        {
          data: "time",
          render: function (data) {
            return data.toString().substring(4, 16);
          },
        },
        { data: "speed" },
        { data: "latitude" },
        { data: "longitude" },
        { data: "battery" },
        { data: "ignition" },
      ],
      dom: "Bfrtip",
      buttons: ["copy", "csv", "excel", "pdf", "print"],
    });
  }

  $("#user-search-btn").click(function (e) {
    e.preventDefault();
    $("#example").dataTable().fnDestroy();
    var bus_id = $("#bus_id").val();
    var start = $("#start_date").val();
    var end = $("#end_date").val();
    console.log(bus_id);
    if (bus_id !== "") {
      if (start == "" || end == "") {
        show_error({ error: "Dates cannot be empty" });
      } else {
        $("#error-msg").css({ visiblity: "hidden" });
        start = preformatdate(start);
        end = preformatdate(end);
        getDataFromApi(start, end, bus_id);
      }
    } //else
    else {
      show_error({ error: "Bus no can't be empty" });
    }
  });
});
