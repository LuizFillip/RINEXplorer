def test_length_of_epoch(count, epoch_section):
    
    assert sum(count.values()) == len(epoch_section)
    