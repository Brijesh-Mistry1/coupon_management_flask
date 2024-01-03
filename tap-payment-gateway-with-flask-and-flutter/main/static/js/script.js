// TOGGLE SIDEBAR
const menuBar = document.querySelector('#content nav .bx.bx-menu');
const sidebar = document.getElementById('sidebar');
let usage_chart = null;
let usage_chart_config = null;
let payment_chart = null;
let payment_chart_config = null;
yearList = []
monthList = []
daysList = []
yearsList = []
couMonthList = []
couDaysList = []
couponList = []
couYearsList = []

window.addEventListener('load', function () {
    if (window.innerWidth <= 768) {
        sidebar.classList.add('hide');
    }
});

menuBar.addEventListener('click', function () {
    sidebar.classList.toggle('hide');
})

window.addEventListener('resize', function () {
    if (window.innerWidth <= 768) {
        sidebar.classList.add('hide');
    } else {
        sidebar.classList.remove('hide');
    }
});


const searchForm = document.querySelector('#content nav form');


// const switchMode = document.getElementById('switch-mode');

// switchMode.addEventListener('change', function () {
//     if(this.checked) {
//         document.body.classList.add('dark');
//     } else {
//         document.body.classList.remove('dark');
//     }
// })

function copyCoupon(code){
    navigator.clipboard.writeText(code);
    var cpnBtn = document.getElementById("cpnBtn-"+code);
    cpnBtn.innerHTML ="COPIED";
    setTimeout(function(){
        cpnBtn.innerHTML="COPY CODE";
    }, 3000);
}

function addDatesToSelect(selectId, values){
    const select = $(`#${selectId}`);
    select.empty()
    select.append(`<option value=''>Select</option>`);
    values.forEach(value => {
        select.append(`<option value=${value}>${value}</option>`);
    });
}


function get_payments_filters(){
    const yearVal = $('#year-filter').val()
    const monthVal = $('#month-filter').val()
    // const dateVal = $('#date-filter').val()
    filters = '?'
    if (monthVal){
        filters = filters + 'month=' + monthVal +'&year=' + yearVal
    }
    else if (yearVal){
        filters = filters + 'year=' + yearVal
    }
    $.ajax({
        url: '/dashboard/api/payments_filters' + filters,
        traditional: true,
        type: 'GET',
        success: function (msg) {
            if ('years' in msg){
                yearsList = msg['years']
                addDatesToSelect('year-filter', msg['years']);
            }else if('months' in msg){
                monthList = msg['months']
                addDatesToSelect('month-filter', monthList);
                $('#month-filter').prop('disabled', false);
            }else if('days' in msg){
                daysList = msg['days']
                addDatesToSelect('date-filter', daysList);
                $('#date-filter').prop('disabled', false);
            }
        }
    })
}

$('#year-filter').on('change', function() {
    $('#month-filter').empty().prop('disabled', true)
    $('#date-filter').empty().prop('disabled', true)
    $('#month-filter').append(`<option value=''>Select</option>`);
    $('#date-filter').append(`<option value=''>Select</option>`);
    get_payments_filters()
});

// Populate the date select based on the selected month
$('#month-filter').on('change', function() {
    $('#date-filter').empty().prop('disabled', true)
    $('#date-filter').append(`<option value=''>Select</option>`);
    get_payments_filters()
});

function get_coupons_usage_filters(){
    const yearVal = $('#usage-year-filter').val()
    const monthVal = $('#usage-month-filter').val()
    // const dateVal = $('#date-filter').val()
    filters = '?'
    if (monthVal){
        filters = filters + 'month=' + monthVal +'&year=' + yearVal
    }
    else if (yearVal){
        filters = filters + 'year=' + yearVal
    }
    $.ajax({
        url: '/dashboard/api/coupons_usage_filters' + filters,
        traditional: true,
        type: 'GET',
        success: function (msg) {
            if ('years' in msg){
                couYearsList = msg['years']
                addDatesToSelect('usage-year-filter', msg['years']);
            }else if('months' in msg){
                couMonthList = msg['months']
                addDatesToSelect('usage-month-filter', couMonthList);
                $('#usage-month-filter').prop('disabled', false);
            }else if('days' in msg){
                couDaysList = msg['days']
                addDatesToSelect('usage-date-filter', couDaysList);
                $('#usage-date-filter').prop('disabled', false);
            }

            if (('coupons' in msg) && (couponList.length <= 0)){
                couponList = msg['coupons']
                $('#coupon-filter').empty()
                $('#coupon-filter').append(`<option value=''>Select</option>`)
                for (i=0;i<couponList.length;i++){
                    coupon = couponList[i]
                    $('#coupon-filter').append(`<option value=${coupon[0]}>${coupon[1]}</option>`);
                }
            }
        }
    })
}

// Populate the months select based on the selected year
$('#usage-year-filter').on('change', function() {
    $('#usage-month-filter').empty().prop('disabled', true)
    $('#usage-date-filter').empty().prop('disabled', true)
    $('#usage-month-filter').append(`<option value=''>Select</option>`);
    $('#usage-date-filter').append(`<option value=''>Select</option>`);
    get_coupons_usage_filters()
});

// Populate the date select based on the selected month
$('#usage-month-filter').on('change', function() {
    $('#usage-date-filter').empty().prop('disabled', true)
    $('#usage-date-filter').append(`<option value=''>Select</option>`);
    get_coupons_usage_filters()
});

function createUsageBarChart(){
    filter = '?'
    selected_year = $('#usage-chart-year').val()
    filter = filter + 'year=' + selected_year

    $.ajax({
        url: '/dashboard/api/usage_chart_data' + filter,
        traditional: true,
        type: 'GET',
        success: function (msg) {
            var canvas = document.getElementById('usage-bar-chart');
            if (canvas) {
                var chart = Chart.getChart(canvas);
                // If a chart exists, destroy it
                if (chart) {
                  chart.destroy();
                }
            }
            var bar_ctx = document.getElementById('usage-bar-chart').getContext('2d');
            const background_1 = bar_ctx.createLinearGradient(0, 0, 0, 600);
            background_1.addColorStop(0, '#ee95ef');
            background_1.addColorStop(1, 'blue');
            var data = {
                labels: msg['months'],
                datasets: [
                    {
                        type: 'bar',
                        label: 'Coupons used in this month',
                        data: msg['months_count'],
                        backgroundColor: background_1,
                        borderColor: background_1,
                    }
                ]
            };

            usage_chart_config = {
                type: 'bar',
                data,
                options: {
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: {
                        y: {
                            grid: {
                                display: false // Hide x-axis grid lines
                            },
                            title: {
                                color: 'black',
                                display: true,
                                text: "No. of Usage",
                                font: {
                                    size: 14
                                },
                            },
                            ticks: {
                                color: '#black',
                                font: {
                                    size: 12
                                }
                            },
                            type: 'linear',
                            display: true,
                            position: 'left',
                          },
                        x: {
                            grid: {
                                display: false // Hide x-axis grid lines
                            },
                            title: {
                                color : 'black',
                                display: true,
                                text: "Months",
                                font: {
                                    size: 14
                                },
                            },
                            ticks: {
                                    color: 'black',
                                    font: {
                                        size: 12
                                    }
                                }
                        }
                    }
                }
            };
            usage_chart = new Chart(
                document.getElementById('usage-bar-chart'),
                usage_chart_config
            );
        }
    })
}

function createPaymentBarChart(){
    filter = '?'
    selected_year = $('#payment-chart-year').val()
    filter = filter + 'year=' + selected_year

    $.ajax({
        url: '/dashboard/api/payment_chart_data' + filter,
        traditional: true,
        type: 'GET',
        success: function (msg) {
            var canvas = document.getElementById('payment-bar-chart');
            if (canvas) {
                var chart = Chart.getChart(canvas);
                // If a chart exists, destroy it
                if (chart) {
                  chart.destroy();
                }
            }
            var bar_ctx = document.getElementById('payment-bar-chart').getContext('2d');
            const background_1 = bar_ctx.createLinearGradient(0, 0, 0, 600);
            background_1.addColorStop(0, '#ee95ef');
            background_1.addColorStop(1, 'blue');
            var data = {
                labels: msg['months'],
                datasets: [
                    {
                        type: 'bar',
                        label: 'Total Payment',
                        data: msg['total_amount'],
                        backgroundColor: background_1,
                        borderColor: background_1,
                    }
                ]
            };

            payment_chart_config = {
                type: 'bar',
                data,
                options: {
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: {
                        y: {
                            grid: {
                                display: false // Hide x-axis grid lines
                            },
                            title: {
                                color: 'black',
                                display: true,
                                text: "Total Payment",
                                font: {
                                    size: 14
                                },
                            },
                            ticks: {
                                color: '#black',
                                font: {
                                    size: 12
                                }
                            },
                            type: 'linear',
                            display: true,
                            position: 'left',
                          },
                        x: {
                            grid: {
                                display: false // Hide x-axis grid lines
                            },
                            title: {
                                color : 'black',
                                display: true,
                                text: "Months",
                                font: {
                                    size: 14
                                },
                            },
                            ticks: {
                                    color: 'black',
                                    font: {
                                        size: 12
                                    }
                                }
                        }
                    }
                }
            };
            payment_chart = new Chart(
                document.getElementById('payment-bar-chart'),
                payment_chart_config
            );
        }
    })
}