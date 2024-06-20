import brotli
import base64


def decompress_string(compressed_string):

    compressed_data = base64.b64decode(compressed_string.encode('utf-8'))
    decompressed_data = brotli.decompress(compressed_data)
    decompressed_string = decompressed_data.decode('utf-8')

    return decompressed_string


# Example usage
compressed_string = "LoremipsumdolorsitametconsecteturadipiscingelitseddoeiusmodtemporincididuntutlaboreetdoloremagnaaliquautenimadminimveniamquisnostrudexercitationullamcolaborisnisiutaliquipexeacommodoconsequatautiruredolorinreLoremipsumdolorsitametconsecteturadipiasdf"
decompressed_string = decompress_string(compressed_string)

print("Decompressed String:", decompressed_string)
print("Length of Decompressed String:", len(decompressed_string))
