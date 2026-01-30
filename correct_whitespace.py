from whitespace_correction import WhitespaceCorrector

corrector = WhitespaceCorrector.from_pretrained("eo_large_byte", device="cpu")
dirty = "With the ope ning of the cou ntry in 1876, know ledge of the many momen tous c hanges, inclu ding in warfare, th at ha d been occurring in west ern Europe during the past several centuries beg an to fl ow into Korea and take root."
clean = corrector.correct_text(dirty)
print(clean)
