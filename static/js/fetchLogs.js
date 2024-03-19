$(document).ready(function() {
    $('.block').click(function() {
        var awsAccount = $(this).attr('id');
        fetchLogs(awsAccount);
    });
});

function fetchLogs(awsAccount) {
    $.get(`/product/A4S/${awsAccount}`, function(data) {
        $('#logsContainer ul').empty(); // Clear existing logs

        // Display Windows Update Information
        $('#logsContainer ul').append('<li>Windows Update Information</li>');
        data.windows_update_information.forEach(update => {
            $('#logsContainer ul').append('<li>' + update + '</li>');
        });

        // Display Recently Installed Software
        $('#logsContainer ul').append('<li>Recently Installed Software</li>');
        $('#logsContainer ul').append('<li>' + data.recently_installed_software + '</li>');

        // Display All Installed Software on the Server
        $('#logsContainer ul').append('<li>All Installed Software on the Server</li>');
        $('#logsContainer ul').append('<li>' + data.all_installed_software + '</li>');
    });
}
