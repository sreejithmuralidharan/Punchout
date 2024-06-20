import brotli
import base64

def compress_string(input_string):
    compressed_data = brotli.compress(input_string.encode('utf-8'))
    compressed_base64 = base64.b64encode(compressed_data).decode('utf-8')
    
    return compressed_base64

# Example usage
original_string = "LoremipsumdolorsitametconsecteturadipiscingelitseddoeiusmodtemporincididuntutlaboreetdoloremagnaaliquautenimadminimveniamquisnostrudexercitationullamcolaborisnisiutaliquipexeacommodoconsequatautiruredolorinreLoremipsumdolorsitametconsecteturadipiasdf"
compressed_string = compress_string(original_string)

print("Original String:", original_string)
print("Length of Original String:", len(original_string))

print("Compressed String:", compressed_string)
print("Length of Compressed String:", len(compressed_string))


