# CEEFAX

This is a set of Python3 scripts which generate a Ceefax-like teletext
service from the following websites:

* BBC News
* BBC Sport

It can be configured using the YAML file `teletext.yaml`.

The output is in the "Viewdata escaped" version of the [TTI file
format](https://zxnet.co.uk/teletext/documents/ttiformat.pdf).

## Modules required to use

* AdvancedHTMLParser, to extract information from HTML pages

      pip3 install AdvancedHTMLParser

  NB. There's a bug in AdvancedHTMLParser:
  https://github.com/kata198/AdvancedHTMLParser/pull/12
  
  Run
  ```
  pico +1272 ~/.local/lib/python3.7/site-packages/AdvancedHTMLParser/Parser.py
  ```
  and change "self.useIndex" to "useIndex".


* CacheControl, to cache fetched pages.  Filecache stores the contents
  in the fileystem
  
      pip3 install CacheControl[filecache]
      
* feedparser, to fetch and parse RSS feeds.

      pip3 install feedparser

* PyYAML, to read the configuration file.

      pip3 install PyYAML

## Credits

I'm indebted to Nathan for originally writing `makeceefax.php`, and
for his subsequent help and encouragement.

* https://github.com/nat2001/makeceefax
* https://www.nathanmediaservices.co.uk/projects/projects.php?link=files/makeceefax

## Other resources

Teletext on the Raspberry Pi

* [vbit2](https://github.com/peterkvt80/vbit2)
* [raspi-teletext](https://github.com/ali1234/raspi-teletext/)
* [set_overscan](https://github.com/ukscone/set_overscan)
* [Raspberry Pi composite
  cables](https://uk.rs-online.com/web/p/products/8326278/)

  
