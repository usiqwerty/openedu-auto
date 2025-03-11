import json
import logging

import config
from openedu.oed_parser import VerticalBlock


class LocalApiStorage:
    blocks: dict[str, VerticalBlock]

    def __init__(self, blocks: dict | None = None):
        if blocks is None:
            try:
                with open(config.blocks_fn, encoding='utf-8') as f:
                    self.blocks = {k: VerticalBlock(**json.loads(v)) for k, v in json.load(f).items()}
            except FileNotFoundError:
                self.blocks = {}
        else:
            self.blocks = blocks

    def is_block_complete(self, block_id: str):
        return self.blocks[block_id].complete

    def mark_block_as_completed(self, block_id: str):
        if not config.config.get('restrict-actions'):
            if block_id in self.blocks:
                self.blocks[block_id].complete = True
                logging.info("Block completed")
            else:
                logging.warning("block that we are checking is not saved, this should not have happened")

    def save(self):
        with open(config.blocks_fn, 'w', encoding='utf-8') as f:
            json.dump({k: v.json() for k, v in self.blocks.items()}, f)
