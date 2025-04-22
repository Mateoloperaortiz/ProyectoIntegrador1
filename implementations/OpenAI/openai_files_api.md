# Files

Files are used to upload documents that can be used with features like Assistants, Fine-tuning, and Batch API.

## Upload File

**POST** `https://api.openai.com/v1/files`

Upload a file that can be used across various endpoints. Individual files can be up to 512 MB, and the size of all files uploaded by one organization can be up to 100 GB.

The Assistants API supports files up to 2 million tokens and of specific file types. See the Assistants Tools guide for details.

The Fine-tuning API only supports `.jsonl` files. The input also has certain required formats for fine-tuning chat or completions models.

The Batch API only supports `.jsonl` files up to 200 MB in size. The input also has a specific required format.

Please contact us if you need to increase these storage limits.

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | file | Required | The File object (not file name) to be uploaded. |
| `purpose` | string | Required | The intended purpose of the uploaded file. One of: <br>- `assistants`: Used in the Assistants API<br>- `batch`: Used in the Batch API<br>- `fine-tune`: Used for fine-tuning<br>- `vision`: Images used for vision fine-tuning<br>- `user_data`: Flexible file type for any purpose<br>- `evals`: Used for eval data sets |

### Returns

The uploaded File object.

### Example Request

```python
from openai import OpenAI
client = OpenAI()

client.files.create(
  file=open("mydata.jsonl", "rb"),
  purpose="fine-tune"
)
```

### Response

```json
{
  "id": "file-abc123",
  "object": "file",
  "bytes": 120000,
  "created_at": 1677610602,
  "filename": "mydata.jsonl",
  "purpose": "fine-tune"
}
```

## List Files

**GET** `https://api.openai.com/v1/files`

Returns a list of files.

### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `after` | string | Optional | - | A cursor for use in pagination. `after` is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include after=obj_foo in order to fetch the next page of the list. |
| `limit` | integer | Optional | 10000 | A limit on the number of objects to be returned. Limit can range between 1 and 10,000, and the default is 10,000. |
| `order` | string | Optional | desc | Sort order by the created_at timestamp of the objects. `asc` for ascending order and `desc` for descending order. |
| `purpose` | string | Optional | - | Only return files with the given purpose. |

### Returns

A list of File objects.

### Example Request

```python
from openai import OpenAI
client = OpenAI()

client.files.list()
```

### Response

```json
{
  "data": [
    {
      "id": "file-abc123",
      "object": "file",
      "bytes": 175,
      "created_at": 1613677385,
      "filename": "salesOverview.pdf",
      "purpose": "assistants"
    },
    {
      "id": "file-abc123",
      "object": "file",
      "bytes": 140,
      "created_at": 1613779121,
      "filename": "puppy.jsonl",
      "purpose": "fine-tune"
    }
  ],
  "object": "list"
}
```

## Retrieve File

**GET** `https://api.openai.com/v1/files/{file_id}`

Returns information about a specific file.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_id` | string | Required | The ID of the file to use for this request. |

### Returns

The File object matching the specified ID.

### Example Request

```python
from openai import OpenAI
client = OpenAI()

client.files.retrieve("file-abc123")
```

### Response

```json
{
  "id": "file-abc123",
  "object": "file",
  "bytes": 120000,
  "created_at": 1677610602,
  "filename": "mydata.jsonl",
  "purpose": "fine-tune"
}
```

## Delete File

**DELETE** `https://api.openai.com/v1/files/{file_id}`

Delete a file.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_id` | string | Required | The ID of the file to use for this request. |

### Returns

Deletion status.

### Example Request

```python
from openai import OpenAI
client = OpenAI()

client.files.delete("file-abc123")
```

### Response

```json
{
  "id": "file-abc123",
  "object": "file",
  "deleted": true
}
```

## Retrieve File Content

**GET** `https://api.openai.com/v1/files/{file_id}/content`

Returns the contents of the specified file.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_id` | string | Required | The ID of the file to use for this request. |

### Returns

The file content.

### Example Request

```python
from openai import OpenAI
client = OpenAI()

content = client.files.content("file-abc123")
```

## The File Object

The File object represents a document that has been uploaded to OpenAI.

| Field | Type | Description |
|-------|------|-------------|
| `bytes` | integer | The size of the file, in bytes. |
| `created_at` | integer | The Unix timestamp (in seconds) for when the file was created. |
| `expires_at` | integer | The Unix timestamp (in seconds) for when the file will expire. |
| `filename` | string | The name of the file. |
| `id` | string | The file identifier, which can be referenced in the API endpoints. |
| `object` | string | The object type, which is always `file`. |
| `purpose` | string | The intended purpose of the file. Supported values are `assistants`, `assistants_output`, `batch`, `batch_output`, `fine-tune`, `fine-tune-results` and `vision`. |
| `status` | string | **Deprecated**. The current status of the file, which can be either `uploaded`, `processed`, or `error`. |
| `status_details` | string | **Deprecated**. For details on why a fine-tuning training file failed validation, see the `error` field on `fine_tuning.job`. |

### Example File Object

```json
{
  "id": "file-abc123",
  "object": "file",
  "bytes": 120000,
  "created_at": 1677610602,
  "expires_at": 1680202602,
  "filename": "salesOverview.pdf",
  "purpose": "assistants"
}
```