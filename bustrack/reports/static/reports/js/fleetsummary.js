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
  function getDataFromAPI(routeId) {
    let config = {
      headers: {
        Authorization:
          "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1ODkxNzIyOTUsIm5iZiI6MTU4OTE3MjI5NSwianRpIjoiOTJjMGQ1MWUtMGI1NC00OTIwLTlhMWQtN2I1MTk3M2ZkODQ3IiwiaWRlbnRpdHkiOjIsImZyZXNoIjpmYWxzZSwidHlwZSI6ImFjY2VzcyJ9.51ZMsgFF61frmYOTijjmyg_bsVkF3DId6pU9LbAsCQ8",
      },
      params: { routeId: routeId },
    };
    axios
      .get(
        "http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/reports/fleet",
        config
      )
      .then(function (response) {
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
    console.log("table called");
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
    console.log(bus_id);
    if (bus_id !== "") {
      getDataFromAPI(bus_id);
    } else {
      show_error({ error: "Bus no can't be empty" });
    }
  });
});
