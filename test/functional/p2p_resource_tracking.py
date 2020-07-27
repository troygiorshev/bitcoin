from time import sleep

from test_framework.mininode import P2PDataStore
from test_framework.test_framework import BitcoinTestFramework

class ResourceTrackingTest(BitcoinTestFramework):
    def set_test_params(self):
        self.num_nodes = 1
        self.setup_clean_chain = True

    def run_test(self):
        for _ in range(100):
            conn = self.nodes[0].add_p2p_connection(P2PDataStore())
            conn.sync_with_ping(timeout=1)
            self.nodes[0].disconnect_p2ps()
            sleep(0.2)

if __name__ == '__main__':
    ResourceTrackingTest().main()
