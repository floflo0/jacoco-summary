# JaCoCo Summary

Display [JaCoCo](https://www.jacoco.org/jacoco/) test coverage result in a fancy
table in the terminal.

## Output example

```
┌──────────────┬─────────────────┬─────────────────┬─────────────────┐
│ Name         │ Branch          │ Line            │ Method          │
├──────────────┼─────────────────┼─────────────────┼─────────────────┤
│ test2.Class2 │ ━━━━━━━━━━  n/a │ ━━━━━━━━━━   0% │ ━━━━━━━━━━   0% │
│ test2.Class1 │ ━━━━━━━━━━   0% │ ━━━━━━━━━━   0% │ ━━━━━━━━━━   0% │
│ test1.Class1 │ ━━━━━━━━━━ 100% │ ━━━━━━━━━━ 100% │ ━━━━━━━━━━ 100% │
│ test1.Class2 │ ━━━━━╺━━━━  50% │ ━━━━━╺━━━━  60% │ ━━━━━━━╺━━  75% │
└──────────────┴─────────────────┴─────────────────┴─────────────────┘
```

## Usage

- Run your tests with maven

```sh
mvn test
```

- Display the result

```sh
jacoco-summary
```

### Help

```
usage: jacoco-summary [-h] [-f FILE] [-v] {package,class,file} ...

Display JaCoCo test coverage result in a fancy way.

options:
  -h, --help            show this help message and exit
  -f, --file FILE       the path JaCoCo report xml file to use
  -v, --version         show program's version number and exit

subcommands:
  {package,class,file}
    package             print the summary of a specific package
    class               print the summary of a specific class
    file                print the summary per files
```
