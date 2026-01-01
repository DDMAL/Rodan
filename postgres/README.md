# Rodan main database
> From https://github.com/DDMAL/Rodan/wiki/Repository-Structure

- The `maintenance` folder is a collection of database maintenance scripts. These are vital to backups, do not change them unless you know what you are doing.
- Rodan uses Redis to query data from `postgres`, plus some perks such as data caching.  