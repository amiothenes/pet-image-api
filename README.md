
# Pet Image API

This project implements a fully serverless pet image API using AWS services (Lambda, API Gateway, S3), deployed via CloudFormation. It handles images labeled as either “cat” or “dog.” Users are able to upload labeled images, and later retrieve a randomly selected image based on a specific label. The source code provides a YAML template file for CloudFormation and the Lambda Python codes for uploading and getting functionalities.




## Features & Design Choices

- Uploads cat or dog images with optional weight via query string in the REST API url.
- Only accepts .jpg, .png, .webp formats.
- Retrieves a random image from S3 using weighted probability.
- Deployable via AWS CloudFormation (provision all infrastructure: S3, Lambda, IAM, API Gateway)
- Image weights stored in S3 object metadata (simple, scalable)
- Query string used for label and weight


## Architecture Design Plan

![architecture plan](https://i.imgur.com/UwdGnG9.png)


## Usage/Examples

- Upload: `POST https://YOUR_API_ID.execute-api.us-east-2.amazonaws.com/dev/upload?label=cat&weight=5 --data-binary "@C:\..."`
- Get random: `GET https://YOUR_API_ID.execute-api.us-east-2.amazonaws.com/dev/random?label=cat --output "C:\..."`

This would be used with a front-end app that would use the API and from it's headers discern what is the extension of the image, since output can be of various types.
Image binary limit size of 6MB due to API Gateway and Lambda. Testing with `curl -X`.
## Cost Estimation
Costs retrieved from Amazon's respective AWS pricing:
- [S3 Pricing](https://aws.amazon.com/s3/pricing/)
- [Lambda](https://aws.amazon.com/lambda/pricing/)
- [API Gateway](https://aws.amazon.com/api-gateway/pricing/) 

### Assumptions
* Number of active users per month
* Each user uploads 1 image and retrieves 4 images (5 API calls total) and no delete
* Images are \~300 KB in size on average
* Using x86 Lambda at 128MB memory, running \~100ms per call
* No API Gateway caching
* All S3 files are retained (not deleted)
* US East (Ohio) region
* Excludes the tree tier except in Tiny, which makes it a little cheaper

### Formulas
#### S3 Storage
`1000 images × 300 KB = 300,000 KB = ~300 MB`
#### Lambda
`GB-seconds = requests × duration × memory in GB`
where the memory is 0.125 GB

### Small App Estimate (with no free tier)
* 1000 images × 300 KB = 300,000 KB = ~300 MB for each image. 1.5 GB if each user uploads 5 images.
* 1000 users × 5 calls each = 5,000 requests
* 5000 × 100 ms = 500,000 ms total = 500 seconds total
* GB-seconds = 500 × 0.125 = 62.5 GB-s
* 62.5 × 0.0000166667 ≈ $0.00 and it's the same even with x5

| Service         | Calculation                                                        | Est. Cost  |
| --------------- | ------------------------------------------------------------------ | ---------- |
| **S3**          | 1.5 GB × \$0.023/GB                                                | \$0.035    |
| **Lambda**      | 500 × 0.125 = 62.5 GB-s → 62.5* $0.00/GB-s | \$0.00     |
| **API Gateway** | 5,000 API calls → \$3.50 / million × 0.005                         | \$0.018    |
| **Total**       |                                                                    | **\$0.05** |

### Conclusion

| Usage Level            | Users/mo | API Calls/mo | S3 Storage | Lambda GB-seconds | API Gateway Cost | **Est. Total Cost** |
| ---------------------- | -------- | ------------ | ---------- | ----------------- | ---------------- | ------------------- |
| **Tiny (dev/testing)** | 100      | 500          | \~30 MB    | \~6.25            | \~\$0.00 (free)  | **\$0.00**          |
| **Small App**          | 1,000    | 5,000        | \~300 MB   | \~62.5            | \~\$0.02         | **\$0.04**          |
| **Medium App**         | 10,000   | 50,000       | \~3 GB     | \~625             | \~\$0.18         | **\$0.25**          |
| **Large App**          | 100,000  | 500,000      | \~30 GB    | \~6,250           | \~\$1.75         | **\$2.54**          |

Even at 10,000 users, this serverless architecture is very cheap — under \$0/month. But this only assumes low levels of activity per user. More active usage averages could multiply the costs. That case would still be very cost efficient for a severless solution.

Scalability: the system scales linearly:
* **API calls** scale with usage
* **Lambda cost** scales with number of requests × memory × time
* **S3** scales with stored image data

## Challenges Faced
- Passing base64-encoded images through API Gateway is tricky
- Had to set up API Gateway binary media types correctly but also had to understand the logs which I had many errors along the way
- Lambda needed to handle base64 decode and image magic headers
- Tested for every edge case (empty bucket, 400s codes etc)
- Storing weight in S3 metadata is simple but not super scalable if you later store millions of images
- Could move metadata to somewhere else like parameters hub or another database
