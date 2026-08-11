# veritasium-unshort

This repository is a personal attempt to automate the process of converting the shortened URLs in the reference document of [Veritasium YouTube channel](https://www.youtube.com/@veritasium) into their original (redirected) links.

> [!IMPORTANT]
> This code in this repository was created solely using an LLM. So, it is important to be aware of this before using it.
---
<table>
<tr>
<td>
<img src="./img/original.png">
<td><img src="./img/image.png"></td>
</td>
</tr>
</table>

## Motive
Since the links in the reference list for each Veritasium video have been put as _https:ve42.co/..._ (their own redirecting domain), there is a **greater chance of losing access to those references in the future due to some reasons**.

So, I thought that it would be a more permanent solution to this problem to convert those shortened links into their original form.

## What you will need to run

- Python 3.12
- Obsidian _(for converting into PDFs)_

## Working
1. After you run the program, it asks for the YouTube URL that you want to get the reference from.

2. It fetches the description and puts it in a JSON file called **description_segments.json**.

3. It splits the description of the video into multiple segments.

4. It asks which segment you want to include in the final reference Markdown file.

5. It may or may not automatically create a file name related to the video, and it will convert those links _(https://ve42.co...)_ into their original form.

6. Finally, it prompts the user for any modifications to the file.

7. If yes, it finishes the whole process by converting the MD into a PDF file using Obsidian.

## Usage

1. Install **yt_dlp**, **requests** packages using pip installer in a folder.

2. Run the _veritasium.py_ file inside the folder using the following command.
`python3.12 veritasium.py`

## Flow design

![architecture](./img/architecture.png)

## License

MIT License
