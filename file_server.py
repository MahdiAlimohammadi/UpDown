import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse

class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
    def list_directory(self, path):
        """Generate a directory listing with upload form, delete functionality, and better UI."""
        try:
            file_list = os.listdir(path)
        except OSError:
            self.send_error(404, "No permission to list directory")
            return None

        # HTML template
        rows = "".join(
            f"""
            <tr>
                <td><a href="{urllib.parse.quote(file)}" download>{file}</a></td>
                <td><button onclick="deleteFile('{file}')">Delete</button></td>
            </tr>
            """
            for file in file_list
        )

        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>File Server</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f9f9f9;
                    color: #333;
                }}
                h1 {{
                    text-align: center;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                th, td {{
                    padding: 10px;
                    border: 1px solid #ccc;
                    text-align: left;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
                form {{
                    margin: 20px 0;
                }}
                .progress {{
                    width: 100%;
                    background-color: #f3f3f3;
                    height: 10px;
                    border-radius: 5px;
                    margin-top: 10px;
                }}
                .progress-bar {{
                    height: 10px;
                    width: 0;
                    background-color: #4caf50;
                    transition: width 0.4s;
                }}
            </style>
            <script>
                function deleteFile(filename) {{
                    fetch(`/delete?filename=${{encodeURIComponent(filename)}}`, {{ method: 'DELETE' }})
                        .then(response => {{
                            if (response.ok) {{
                                alert(`File '${{filename}}' deleted successfully.`);
                                location.reload();
                            }} else {{
                                alert('Failed to delete file.');
                            }}
                        }});
                }}

                function uploadFile(event) {{
                    event.preventDefault();
                    const fileInput = document.getElementById('file-input');
                    const file = fileInput.files[0];
                    if (!file) {{
                        alert('Please select a file to upload.');
                        return;
                    }}

                    const formData = new FormData();
                    formData.append('file', file);

                    const xhr = new XMLHttpRequest();
                    xhr.open('POST', '/', true);

                    xhr.upload.onprogress = function (event) {{
                        if (event.lengthComputable) {{
                            const percent = (event.loaded / event.total) * 100;
                            document.getElementById('progress-bar').style.width = percent + '%';
                        }}
                    }};

                    xhr.onload = function () {{
                        if (xhr.status === 201) {{
                            alert('File uploaded successfully.');
                            location.reload();
                        }} else {{
                            alert('Failed to upload file.');
                        }}
                    }};

                    xhr.send(formData);
                }}
            </script>
        </head>
        <body>
            <h1>File Server</h1>
            <table>
                <thead>
                    <tr>
                        <th>Filename</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
            <form onsubmit="uploadFile(event)">
                <h2>Upload a File</h2>
                <input type="file" id="file-input" name="file">
                <button type="submit">Upload</button>
                <div class="progress">
                    <div id="progress-bar" class="progress-bar"></div>
                </div>
            </form>
        </body>
        </html>
        """
        encoded = html.encode("utf-8", "surrogateescape")
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)
        return None

    def do_POST(self):
        """Handle file uploads."""
        content_length = int(self.headers["Content-Length"])
        boundary = self.headers["Content-Type"].split("boundary=")[-1].encode()
        data = self.rfile.read(content_length)
        parts = data.split(b"--" + boundary)

        for part in parts:
            if b"Content-Disposition" in part:
                disposition = part.split(b"\r\n")[1]
                if b"filename=" in disposition:
                    filename = disposition.split(b"filename=")[-1].strip(b'"').decode()
                    file_data = part.split(b"\r\n\r\n", 1)[-1].rsplit(b"\r\n", 1)[0]
                    with open(filename, "wb") as f:
                        f.write(file_data)
                    self.send_response(201)
                    self.end_headers()
                    return

        self.send_response(400)
        self.end_headers()

    def do_DELETE(self):
        """Handle file deletions."""
        parsed_path = urllib.parse.urlparse(self.path)
        filename = urllib.parse.parse_qs(parsed_path.query).get("filename", [None])[0]
        if filename and os.path.exists(filename):
            os.remove(filename)
            self.send_response(200)
        else:
            self.send_response(404)
        self.end_headers()

def run_server(directory, port):
    os.chdir(directory)
    httpd = HTTPServer(("", port), CustomHTTPRequestHandler)
    print(f"Serving directory '{directory}' on port {port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        httpd.server_close()

if __name__ == "__main__":
    run_server("/home/fileserver", 8888)
