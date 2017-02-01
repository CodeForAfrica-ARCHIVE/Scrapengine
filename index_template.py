template = """
 {"type": "add",
  "id":   "%s",
  "fields": {
      "address": "%s",
      "facility": "%s",
      "name": "%s",
      "practice_type": "%s",
      "qualification": "%s",
      "registration_date": "%s",
      "registration_number": "%s",
      "specialty": "%s",
      "sub_specialty": "%s",
      "type": "%s"
  }
 }
"""

delete_template = '{"type": "delete","id":"%s"}'