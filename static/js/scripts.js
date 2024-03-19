function fetchProductLogs(product) {
    fetch(`/product/${product}`)
        .then(response => response.json())
        .then(data => {
            // Process the logs data
            console.log(data);
            // Redirect to a new page or display the logs on the same page as needed
        })
        .catch(error => {
            console.error('Error fetching product logs:', error);
        });
}
