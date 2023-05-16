$(() => {
  // Define a function that appends data to the #log element on the page
  const appendToLog = (data) => $('#log').append(`${typeof data === 'object' ? JSON.stringify(data) : data}<br />`);

  // Define a function that handles AJAX errors by appending the error response text to the #log element
  const handleAjaxError = (error) => appendToLog(error.responseText);

  // Define a function that makes an AJAX request to the specified URL and appends the response data to the #log element on the page
  const runAjax = (url) => $.get(url).done(appendToLog).fail(handleAjaxError);

  // Define a function that runs the log AJAX request repeatedly every 500ms until it succeeds, and then runs the res AJAX request
  const runLogAjax = () => runAjax('/code/log').fail(() => setTimeout(runLogAjax, 500)).done(runResAjax);

  // Define a function that runs the res AJAX request and appends the response data to the #log element on the page
  const runResAjax = () => runAjax('/code/res');

  // Set the options for the marked library, which is used to parse and render Markdown
  marked.setOptions({
    renderer: new marked.Renderer(),
    highlight: (code) => hljs.highlightAuto(code).value,
    langPrefix: 'hljs language-'
  });

  // Render the Markdown content in the #content element on the page using the marked library
  $('#content').html(marked.parse(`{{ markdown | safe | replace('`','\`') }}`));

  // Add a submit event listener to the #form element on the page
  $('#form').submit((e) => {
    // Prevent the form from submitting normally
    e.preventDefault();

    // Clear the #log element on the page
    $('#log').empty();

    // Serialize the form data and convert it into an object
    const result = $('#form').serializeArray().reduce((acc, { name, value }) => ({
      ...acc,
      [name]: acc[name] ? `${acc[name]},${value}` : value
    }), {});

    // Make an AJAX request to run the code on the server, and append the response data to the #log element on the page
    $.post('/code/run', result).done((data) => {
      appendToLog(data);
      // Start the log AJAX request loop
      runLogAjax()
    }).fail(handleAjaxError);
  });
});
