$(document).ready(function () {
  console.log("jquery loaded");

  $("#error-msg").css({ visibility: "hidden" });

  $("#example").css({ visibility: "hidden" });

  $.fn.dataTable.ext.errMode = "throw";

  $(function () {
    $("#start_date").datetimepicker({
      dateFormat: "yyyy-mm-dd",
      maxDate: $.now(),
      useCurrent: false,
      format: "L",
    });
  });
  $(function () {
    $("#end_date").datetimepicker({
      dateFormat: "YYYY-MM-DD",
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
  function show_data_table(data) {
    $("#example").DataTable({
      responsive: true,
      data: data,
      columns: [
        {
          data: "time",
          render: function (data) {
            return data.toString().substring(4, 16);
          },
        },
        {
          data: "runHrs",
        },
      ],
      dom: "Bfrtip",
      buttons: ["copy", "csv", "excel", "pdf", "print"],
    });
  }
  function getDataFromApi(start, end, routeId) {
    var url =
      "http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/reports/uptime";
    let config = {
      headers: {
        Authorization:
          "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1ODkxNzIyOTUsIm5iZiI6MTU4OTE3MjI5NSwianRpIjoiOTJjMGQ1MWUtMGI1NC00OTIwLTlhMWQtN2I1MTk3M2ZkODQ3IiwiaWRlbnRpdHkiOjIsImZyZXNoIjpmYWxzZSwidHlwZSI6ImFjY2VzcyJ9.51ZMsgFF61frmYOTijjmyg_bsVkF3DId6pU9LbAsCQ8",
      },
      params: {
        fromDate: start,
        toDate: end,
        routeId: routeId,
      },
    };
    axios
      .get(url, config)
      .then(function (response) {
        console.log(response.data);
        if ("error" in response.data) {
          show_error(response.data);
        } else {
          show_data_table(response.data);
        }
      })
      .catch(function (error) {
        console.log(error);
      });
  }
  $("#searchBus").click(function (e) {
    // alert("hello");
    e.preventDefault();
    var start = $("#start_date").val();
    start = preformatdate(start);
    var end = $("#end_date").val();
    end = preformatdate(end);
    console.log(start, end);
    $("#example").dataTable().fnDestroy();
    var routeId = $("#busno").val();

    if (routeId != "") {
      if (start != "" && end != "") {
        $("#error-msg").text("");
        $("#example").css({ visibility: "visible" });
        getDataFromApi(start, end, routeId);
      } else {
        $("#error-msg").text("Dates cannot be empty");
        $("#error-msg").css({ visibility: "visible" });
        $("#error-msg").slideDown(function () {
          setTimeout(function () {
            $("#error-msg").slideUp();
          }, 1000);
        });
      }
    } else {
      $("#error-msg").text("BusNo cannot be empty");
      $("#error-msg").css({ visibility: "visible" });
      $("#error-msg").slideDown(function () {
        setTimeout(function () {
          $("#error-msg").slideUp();
        }, 1000);
      });
    }
  });
});
