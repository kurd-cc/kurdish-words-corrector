# Kurdish words corrector <br>

Correct the typos and the Unicode problems in Kurdish (Kurmanji) by brute forcing and comparing with a dictionary.<br>
The brute forcing has 3 different depths and specific most popular typos like writing `s` instead of `ş` or `e` instead of `ê`.
<br><br>
<strong>Incorrect sentence: </strong>
```text
Reso cu dur.
```
<br>
<strong>Corrected sentence: </strong>

```text
Reşo çû dûr.
```
<br>

### Usage: <br>

```shell script
python kurdish-words-corrector.py -t "Reso cu dur." -o "results.txt"
```

- You can read the results in `yaml` or `json` formats when you didn't include `-o` path.
- The script will save a states file in the same path which include the `json` or `yaml` formated results (it includes some states too).
<br>

An example of the resulted `json`: <br>

```json
{
  "correct_words": [],
  "incorrect_words_with_possible_corrections": [
    {
      "word": "Reso",
      "message": "Is not in our database, and we found similar word/s",
      "status": 1,
      "possibilities": [
        "reşo"
      ]
    },
    {
      "word": "cu",
      "message": "Is not in our database, and we found similar word/s",
      "status": 1,
      "possibilities": [
        "çû"
      ]
    },
    {
      "word": "dur",
      "message": "Is not in our database, and we found similar word/s",
      "status": 1,
      "possibilities": [
        "dûr"
      ]
    }
  ],
  "incorrect_words_without_possible_corrections": [],
  "total_words": 3,
  "total_incorrect": 3,
  "total_incorrect_with_corrections": 3,
  "total_incorrect_without_corrections": 0,
  "incorrect_percentage": 100
}
```

#### Arguments: <br>

| Argument      | Description |
| ----------- | ----------- |
| -w <strong>or</strong> --word    | A word to only get its corrected form      |
| -t <strong>or</strong> --text    | The entered text to correct its words       |
| -o <strong>or</strong> --output | The path of output results file with corrected text        |
| -f <strong>or</strong> --file    | The path of the file to correct its text's words       |
| -d <strong>or</strong> --depth | With the values 1, 2 or 3, to increase the level of brute forcing but also the time it needs to be processed       |
| -p <strong>or</strong> --parser    | The parsing of the outputed file; yaml (default) or json       |
| -wr <strong>or</strong> --workers    | The numbers of workers (threads) that you want to use, default=100      |
