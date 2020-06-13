// Set relative times
window.addEventListener("load", function() {
    const els = document.getElementsByClassName('moment-js-relative-time');
    for (const el of els) {
        const data_timestamp = el.attributes["data-timestamp"].value;
        const timestamp = moment.utc(data_timestamp, moment.ISO_8601, true);
        if (!timestamp.isValid()) {
            this.console.log(`Invalid timestamp: ${data_timestamp}`);
            continue;
        }
        const whenString = timestamp.fromNow();
        el.innerHTML = `(${whenString})`;
    }
});

window.addEventListener("load", function() {
    $('.dcss-datatable').DataTable(
        {
            "scrollX": true,
            "lengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
            "iDisplayLength": 10,
        }
    );
    $('.dcss-datatable-wide').DataTable(
        {
            "scrollX": true,
            "lengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
            "iDisplayLength": 10,
            "ordering": true,
            // Keep the left two columns visible when scrolling sideways
            "fixedColumns": {
                "leftColumns": 2,
            },
        }
    );
    if ($('.dcss-datatable-wide').length)
        $('.container').addClass('container-fluid').removeClass('container');

    $('.dcss-datatable-compact').DataTable(
        {
            "paging": false,
            "searching": false,
            "info": false,
        }
    );
});

function player_search_update(hide_empty)
{
    search_box = $("#player-search");
    query = search_box.val().toUpperCase();
    if (hide_empty)
    {
        search_div = $("#player-search-div");
        if (query == "")
        {
            search_div.hide();
            return;
        }
        search_div.show();
    }

    $("#player-search-div ul li").each(function(i)
        {
            text = $( this ).children("a").text();
            if (text.toUpperCase().startsWith(query))
                $( this ).show();
            else
                $( this ).hide();
        });
}

function clan_search_update(hide_empty)
{
    search_box = $("#clan-search");
    query = search_box.val().toUpperCase();
    if (hide_empty)
    {
        search_div = $("#clan-search-div");
        if (query == "")
        {
            search_div.hide();
            return;
        }
        search_div.show();
    }

    $("#clan-search-div ul li").each(function(i)
        {
            text = $( this ).children("a").text();
            // use matching anywhere in the string for clans
            if (text.toUpperCase().indexOf(query) > -1)
                $( this ).show();
            else
                $( this ).hide();
        });
}
