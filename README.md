### Testspider
 Start spider with 

 ```bash
 scrapy crawl bw 
 ```

To collect the items into a json file use:

```bash
crawl bw -o output.json
```

If you want to set a minimum number of items to collect use:

```bash
crawl bw -o output.json -a min_items=13
```