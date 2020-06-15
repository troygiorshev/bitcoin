// Copyright (c) 2019 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <chainparams.h>
#include <net.h>
#include <protocol.h>
#include <test/fuzz/fuzz.h>

#include <cassert>
#include <cstdint>
#include <limits>
#include <vector>

void initialize()
{
    SelectParams(CBaseChainParams::REGTEST);
}

void test_one_input(const std::vector<uint8_t>& buffer)
{
    V1TransportDeserializer deserializer{Params(), SER_NETWORK, INIT_PROTO_VERSION};
    const char* pch = (const char*)buffer.data();
    size_t n_bytes = buffer.size();
    while (n_bytes > 0) {
        const int handled = deserializer.Read(pch, n_bytes);
        if (handled < 0) {
            break;
        }
        pch += handled;
        n_bytes -= handled;
        if (deserializer.Complete()) {
            const int64_t m_time = std::numeric_limits<int64_t>::max();
            auto result = deserializer.GetMessage(m_time);
            if (result){
                const CNetMessage msg = *result;
                assert(msg.m_command.size() <= CMessageHeader::COMMAND_SIZE);
                assert(msg.m_raw_message_size <= buffer.size());
                assert(msg.m_raw_message_size == CMessageHeader::HEADER_SIZE + msg.m_message_size);
                assert(msg.m_time == m_time);
            }
        }
    }
}
