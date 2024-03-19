$(document).ready(function() {
    $('select[name="customer"]').change(function() {
        var selectedCustomer = $(this).val(); // Get the selected customer
        if (selectedCustomer) {
            fetchLogs(selectedCustomer);
        } else {
            $('.logsContainer').hide();
        }
    });
});

document.addEventListener('DOMContentLoaded', function() {
    var form = document.getElementById('customerForm');
    if (!form) {
        console.error('Form element not found.');
        return;
    }

    var allCustomersButton = document.getElementById('allCustomersButton');
    if (!allCustomersButton) {
        console.error('Button element not found.');
        return;
    }

    allCustomersButton.addEventListener('click', function() {
        console.log('Want for all customers button clicked.');

        // Perform any desired actions here, such as submitting the form
        if (form) {
            form.submit();
        } else {
            console.error('Form element not found.');
        }
    });
});


function handlePredict(event) {
    event.preventDefault(); // Prevent form submission

    // Make an AJAX POST request to the predict route
    $.ajax({
        type: "POST",
        url: "/product/A4S/A4S-Dev-Acc/Predict",
        data: $("#predictForm").serialize(), // Serialize form data
        success: function(response) {
            if (response && response.html_path) {
                // Redirect to the generated HTML page
                window.location.href = response.html_path;
            } else {
                console.error("Invalid response from server.");
            }
        },
        error: function(xhr, status, error) {
            // Handle error gracefully
            console.error("Error:", error);
            // Optionally, display an error message to the user
            alert("An error occurred while processing your request. Please try again later.");
        }
    });
}
