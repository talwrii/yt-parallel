# yt parallel
**@readwithai** - [X](https://x.com/readwithai) - [blog](https://readwithai.substack.com/) - [machine-aided reading](https://www.reddit.com/r/machineAidedReading/) - [📖](https://readwithai.substack.com/p/what-is-reading-broadly-defined
)[⚡️](https://readwithai.substack.com/s/technical-miscellany)[🖋️](https://readwithai.substack.com/p/note-taking-with-obsidian-much-of)

Create parallel lyrics in two languages for a song downloaded from youtube using their autotranslated lyrics.

This is related to the idea of [parallel corpora](https://en.wikipedia.org/wiki/Parallel_text) for language learning. You likely adapt this tool to your use cases - such as burning text into youtube videos.

## Motivation
I want to exercise a lot, but it frequently feels kind of pointless. I am trying to learn
danish so I want to play songs in danish, but I also want to understand the lyrics.
The ideal solution would be have the lyrics while I play - but there is nothing on the meta quest which does this immediately and I want something *now*.

Therefore, the solution I am going for is hanging the lyrics open on a tabet attached to the wall which I can quicky look at. This program is for this. It creates an html page.

## Installation
You can install `yt-parallel` using [pipx](https://github.com/pypa/pipx):
```
pipx install yt-parallel
```

You also must install `yt-dlp` with pipx and `espeak` (you can install this with apt on linux)

## Usage
This tool wraps `yt-dlp` which often needs cookies a browser which has logged into youtube to wor. If you use chrome you need only log into youtube in this browser. For other browsers you can use the `YT_PARALLEL_COOKIES` variable set the `--cookies-from-browser` [option in yt-dlp](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp). Remember to add the browser type like `chromium:` to this string.

You can then run:

```
yt-parallel 'https://www.youtube.com/watch?v=MhghQ3AFCe0' da en
```

If you are learning danish in english.


## Troubleshooting
Errors related to `Too Many Requests` can occur if you are not logged into youtube.
Ensure you are logged in in a browser and try changing `YT_PARALLEL_COOKIES`. You likely want to try getting `yt-dlp` working directly.

If this is still a problem you might like to change the `--impersonate` setting.

```
ERROR: Unable to download video subtitles for 'en': HTTP Error 429: Too Many Requests
```

## Alternatives and prior work
This tool uses yt-dlp and espeak.

There are many commercial interactive tools which provide similar features and allow you to listen to music or watch films while seeing lyrics in two languages. Language reactor is one such example and works with youtube.

[opus](https://opus.nlpl.eu/) provide parallel corpora of sentence pairs (which incidentally can be rebuilt into copmlete parallel corpora for movies).

There are tools for sentence alignment which can be fed books in two languages to create parallel books. You can also buy books in two languages at the same time.

Looks like ffmpeg can extract subtitles from films in different languages  which can then be combined and "burned it".

However, my use case is lyrics that I can look at while playing beat saber.

## About me
I am **@readwithai**. I create tools for reading, research and agency sometimes using the markdown editor [Obsidian](https://readwithai.substack.com/p/what-exactly-is-obsidian).

I also create a [stream of tools](https://readwithai.substack.com/p/my-productivity-tools) that are related to carrying out my work.

I write about lots of things - including tools like this - on [X](https://x.com/readwithai).
My [blog](https://readwithai.substack.com/) is more about reading and research and agency.

I am also interested in [Virtual reality](https://reddit.com/r/vrfit). I also have a personal wiki about using the game Pistol whip for [VR fitness](https://educated-ravioli-5a1.notion.site/Virtual-reality-fitness-with-pistol-whip-2a63b79f2b9d80bba5d1e8b77c70a779).
