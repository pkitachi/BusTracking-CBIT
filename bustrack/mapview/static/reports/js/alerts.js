$(document).ready(function () {
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
  function preformatdate(date) {
    newdate = date.split("/");
    newdate = newdate[2] + "-" + newdate[0] + "-" + newdate[1];
    return newdate;
  }
  function showDataTable(data) {
    // console.log(data);
    $("#example").DataTable({
      data: data,
      order: [[2, "desc"]],

      columns: [
        { data: "IMEI" },
        { data: "alertCode" },
        {
          data: "alertDate",
          render: function (data) {
            return data.toString().substring(4, 16);
          },
        },
        { data: "alertId" },
        { data: "description" },
        { data: "smsStatus" },
      ],
      dom: "Bfrtip",
      buttons: ["copy", "csv", "excel", "pdf", "print"],
    });
  }
  function getDataFromApi(fromDate, toDate, alertCode) {
    if (alertCode == "") {
      var params = {
        fromDate: fromDate,
        toDate: toDate,
      };
    } else {
      var params = {
        fromDate: fromDate,
        toDate: toDate,
        alertCode: alertCode,
      };
    }
    let config = {
      headers: {
        Authorization:
          "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1ODkxNzIyOTUsIm5iZiI6MTU4OTE3MjI5NSwianRpIjoiOTJjMGQ1MWUtMGI1NC00OTIwLTlhMWQtN2I1MTk3M2ZkODQ3IiwiaWRlbnRpdHkiOjIsImZyZXNoIjpmYWxzZSwidHlwZSI6ImFjY2VzcyJ9.51ZMsgFF61frmYOTijjmyg_bsVkF3DId6pU9LbAsCQ8",
      },
      params: params,
    };
    axios
      .get(
        "http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/reports/alerts",
        config
      )
      .then((response) => {
        // console.log(response.data);
        showDataTable(response.data);
      })
      .catch((err) => {
        console.log(err);
      });
  }
  $("#user-search-btn").click(function (e) {
    var start = $("#start_date").val();
    var end = $("#end_date").val();
    var alert_type = $("#alert-type").val();
    if (alert_type == "") {
    }
    // console.log(start);
    if (start == "" || end == "") {
      $("#error-msg").css({ visibility: "visible" });
      $("#error-msg").slideDown(function () {
        setTimeout(function () {
          $("#error-msg").slideUp();
        }, 1000);
      });
    } else {
      $("#error-msg").css({ visiblity: "hidden" });

      e.preventDefault();
      start = preformatdate(start);
      end = preformatdate(end);
      $("#example").css({ visibility: "visible" });
      $("#example").dataTable().fnDestroy();

      getDataFromApi(start, end, alert_type);
      console.log("calling api...");
    } //else
  });
});
