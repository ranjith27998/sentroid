'use strict';
function getCookie(cname) {
  let name = cname + "=";
  let ca = document.cookie.split(';');
  for(let i = 0; i < ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

$(document).ready(function() {
    setTimeout(function() {
    // [ bar-simple ] chart start

    // [ bar-simple ] chart end

    // [ bar-stacked ] chart end


    // [ area-angle-chart ] end

    // [ area-smooth-chart ] end


    // [ line-angle-chart ] end
    // [ line-smooth-chart ] start

    let csrf_token = getCookie("csrftoken");
    console.log(csrf_token)
     $.ajax({
            type: "POST",
            url: "http://192.168.50.109:9001/ai/get_chart/",
              headers: {
                'X-CSRF-TOKEN':csrf_token,
                'Content-Type':'application/json'
    },
    dataType: 'json',
    data: {},
    success: function(res_data){
        Morris.Line({
        element: 'morris-line-smooth-chart',
        data: res_data,
        xkey: 'y',
        redraw: true,
        resize: true,
        ykeys: ['a', 'b', 'c'],
        hideHover: 'auto',
        responsive:true,
        labels: ['POSITIVE', 'NEUTRAL', 'NEGATIVE'],
        lineColors: ['#07f723', '#eff707', '#e80202']
    });

    }
  });
     $.ajax({
            type: "POST",
            url: "http://192.168.50.109:9001/ai/update_tbl/",
              headers: {
                'X-CSRF-TOKEN':csrf_token,
                'Content-Type':'application/json'
    },
    dataType: 'json',
    data: {},
    success: function(res_data){
        console.log("Call Done")

    }
  });
     }, 700);
});
