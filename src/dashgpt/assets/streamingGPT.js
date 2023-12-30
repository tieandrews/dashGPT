window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        streaming_GPT: async function streamingGPT(formatted_context, n_clicks, prompt, streaming_object_id, chat_history) {

            // if prompt is empty, return an empty string and false
            if (prompt === "") {
                return [false, ""];
            }

            // id of the window we want to write the response to
            // you may use dynamically created id's here if you have multiple windows 
            // eg "#response-window-${element_id}"
            const responseWindow = document.querySelector("#" + streaming_object_id);
            // const responseWindow = document.querySelector("#${stream_object_id}");

            // "marked.js" is used to parse the incoming stream
            // it is also a good idea to state in the prompt that the "response should be markdown formatted"
            // this definition changes the color scheme of the parsed code. If your use-case does not include parsing code, you can remove this part, as well as "asssets/external/highlight.min.js" and "asssets/external/markdown-code.css"
            // if your application use-case includes parsing code and wish to change color scheme of the parsed code, you can do so in "asssets/external/markdown-code.css"
            // alternatively, you can go to "https://highlightjs.org/static/demo/" to find a theme you like and then download it from "https://github.com/highlightjs/highlight.js/tree/main/src/styles"
            marked.setOptions({
                highlight: function (code) {
                    return hljs.highlightAuto(code).value;
                }
            });

            // Send the messages to the server to get the streaming response
            // if you have more parameters python side, you can add them to the body
            // eg. body: JSON.stringify({ prompt, parameter1, parameter2 }),
            const response = await fetch("/streaming-chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ prompt, formatted_context, chat_history }),
            });

            // Create a new TextDecoder to decode the streamed response text
            const decoder = new TextDecoder();

            // Set up a new ReadableStream to read the response body
            const reader = response.body.getReader();
            let chunks = "";

            // Read the response stream as chunks and append them to the chat log
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                chunks += decoder.decode(value);
                const htmlText = marked.parse(chunks); // this line will parse the incoming stream as markdown text, using "marked.js" package
                responseWindow.innerHTML = htmlText;
            }

            // Get the generated text from the response window
            // const generatedText = responseWindow.textContent;
            const generatedText = responseWindow.innerHTML;

            // Return the generated text and false to enable the submit button again (disabled=false)
            return [false, generatedText];
        }
    }
});