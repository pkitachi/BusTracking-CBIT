$(document).ready(function () {
  $("#example").css({ visibility: "hidden" });
  function showDataTable(data) {
    $("#example").css({ visibility: "visible" });
    $.fn.dataTable.ext.errMode = "throw";
    $("#example").DataTable({
      responsive: true,
      data: data,
      columns: [
        {
          data: "routeId",
        },
        {
          data: "routeName",
        },
      ],
      dom: "Bfrtip",
      buttons: ["copy", "csv", "excel", "pdf", "print"],
    });
  }
  console.log("jquery loaded");
  let config = {
    headers: {
      Authorization:
        "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1ODkxNzIyOTUsIm5iZiI6MTU4OTE3MjI5NSwianRpIjoiOTJjMGQ1MWUtMGI1NC00OTIwLTlhMWQtN2I1MTk3M2ZkODQ3IiwiaWRlbnRpdHkiOjIsImZyZXNoIjpmYWxzZSwidHlwZSI6ImFjY2VzcyJ9.51ZMsgFF61frmYOTijjmyg_bsVkF3DId6pU9LbAsCQ8",
    },
  };
  axios
    .get(
      "http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/routes",
      config
    )
    .then((response) => {
      showDataTable(response.data);
    })
    .catch((err) => console.log(err));
});
