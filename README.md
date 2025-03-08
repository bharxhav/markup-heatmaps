# Markup Heatmaps!

Markup Heatmaps are designed to visualize large html data scrape.



```python
import os
import sys
sys.path.append("./code")
```

## Part 1: Reading Tags



```python
from tag_reader import TagReader
```


```python
htmls_dir = "./data/htmls"  
doms_dir = "./data/doms"
```


```python
for file in os.listdir(htmls_dir):
    if file.endswith(".html"):
        # check if the file is already processed
        if os.path.exists(os.path.join(doms_dir, file.replace(".html", ".json"))):
            continue

        reader = TagReader(os.path.join(htmls_dir, file))
        dom = reader.parse()
        reader.save_to_file(os.path.join(doms_dir, file.replace(".html", ".json")))

```

### Sample

```json
        },
        {
          "body": [
            {
              "header": [
                {
                  "figure": [
                    {
                      "a": [
                        {
                          "img": []
                        }
                      ]
                    }
                  ]
                },
```

