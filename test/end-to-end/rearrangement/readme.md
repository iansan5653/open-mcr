# Rearrangement Example

This is a simple example of using an arrangment file to score shuffled exams.

Test Form A is the original example, which has questions in 1-2-3 order. The
answer key is defined as:

1. A
2. E
3. A

Test Form B is the same test as Form A, but the questions have been reordered to
1-3-2.

The arrangement file for this looks like:

```csv
Test Form Code, Q1, Q2, Q3
             A,  1,  2,  3
             B,  1,  3,  2
```

Both submission examples given should result in a score of 100% after
rearrangement.
