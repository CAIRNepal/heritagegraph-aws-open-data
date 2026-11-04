# AWS Open Data onboarding checklist

Tracks the steps in the *Onboarding Handbook for Data Providers* (AWS Open Data Sponsorship Program, revised
2025-10-15): <https://assets.opendata.aws/aws-onboarding-handbook-for-data-providers-en-US.pdf>.
Status as of 2026-11-03. Contact for the program: opendata@amazon.com.

## Step 2: Documentation, tutorial and registry entry (handbook §2)

### 2.1 Registry of Open Data entry

The entry lives in the fork [CAIRNepal/open-data-registry](https://github.com/CAIRNepal/open-data-registry)
(`datasets/cair-nepal-heritage-graph.yaml`) and goes to
[awslabs/open-data-registry](https://github.com/awslabs/open-data-registry) as a **draft** pull request.

- [x] **Fix the entry in the fork** (fixed in the local clone and validated on 2026-11-03; commit, push and open the
      draft PR). The previous version failed validation and described the old graph:
  - tags not in `tags.yaml` (only *computer vision*, *natural language processing* and *machine learning* are
    valid, and they don't describe this dataset);
  - `RegistryEntryAdded` and `RegistryEntryLastModified` are missing (required);
  - `ARN` is empty and `Region` is `us-east-2`; the bucket is `cair-nepal-heritage-graph` in **`us-east-1`**;
  - `DataAtWork.Explore` is not a valid field (`Explore` belongs under a resource), and the linked platform
    `https://heritagegraph.cair-nepal.org/` currently returns 404;
  - no tutorial entry: the handbook requires the notebook as the **first** `Tutorials` entry, titled
    "Get To Know A Dataset: [DATASET NAME]";
  - the description mentions Wikidata/OSM links, named graphs and intangible heritage, which this release does
    not contain;
  - `ADXCategories: Resources Data` is the natural-resources category (optional field; consider removing);
  - `License` says CC BY 4.0; the licence is **CC BY-SA 4.0**.
- [x] Point `Documentation` at <https://github.com/CAIRNepal/heritagegraph-aws-open-data> and add the tutorial as the
      first `DataAtWork > Tutorials` entry, titled "Get To Know A Dataset: HeritageGraph", URL
      `https://github.com/CAIRNepal/heritagegraph-aws-open-data/blob/main/cair-nepal-heritage-graph/get-to-know-a-dataset.ipynb`.
- [ ] Email a logo to opendata@amazon.com, **wider than 160 px** (shown at 160 px on the landing page).
- [ ] When everything below is done, take the PR out of draft (handbook §6).

To validate after editing:

```bash
git clone --depth 1 https://github.com/awslabs/open-data-registry && cd open-data-registry
pip install pykwalify requests pyyaml
pykwalify -d datasets/cair-nepal-heritage-graph.yaml -s schema.yaml -e ext.py
```

### 2.2 Descriptive documentation

- [x] [README.md](README.md): bucket layout, access, data dictionary, example queries, limitations, versioning.
      This is the `Documentation` URL in the registry entry.

### 2.3 Tutorial notebook

- [x] [`cair-nepal-heritage-graph/get-to-know-a-dataset.ipynb`](cair-nepal-heritage-graph/get-to-know-a-dataset.ipynb),
      built from the AWS template (<https://github.com/awslabs/open-data-docs/tree/main/get-to-know-a-dataset>),
      answering each template question including the community challenge. Reads from the public bucket; tested
      end to end against `v1.0.0`. Committed without outputs, as the template asks.
- [x] Listed as the first tutorial in the registry entry (see 2.1).

## Step 3: Terms and conditions (handbook §3)

- [ ] Someone at CAIR-Nepal agrees to the program terms
      (<https://aws.amazon.com/opendata/open-data-sponsorship-program/terms/>) via the agreement form
      (<https://pages.awscloud.com/open-data-sponsorship-program.html>). Record the date here.

## Step 4: New AWS account, linked to the program (handbook §4)

- [ ] Create a new AWS account used **only** to host this dataset. Only Amazon S3 may be used in it unless the
      Open Data team agrees otherwise.
- [ ] Email the account number and root email address to opendata@amazon.com.
- [ ] Accept the invitation to the program's AWS Organization (it expires after a few days; leave any other
      Organization first).
- [ ] Email opendata@amazon.com to confirm the account is linked. **Do not upload data until this is confirmed**,
      or the charges are not covered.

The bucket `cair-nepal-heritage-graph` already exists and holds data. Confirm that it is in the linked account
and was created with the program's CloudFormation template (handbook §5), which also sets up access logging,
metrics, Intelligent-Tiering and the SNS topic. If it was created by hand, ask opendata@amazon.com whether to
recreate it from the template.

## Bucket follow-ups (handbook §5 and Appendix A)

Checked anonymously with [`tools/test_s3_public.py`](tools/test_s3_public.py) on 2026-11-03: **5/5 checks pass**
(public read, public listing, anonymous upload blocked, CORS `GET`, CORS preflight).

- [ ] **Content types.** Objects are served as `binary/octet-stream`. Set the right types, so browsers and tools
      handle them correctly (needs credentials for the hosting account):

      ```bash
      B=s3://cair-nepal-heritage-graph/v1.0.0
      aws s3 cp $B/heritagegraph-nepal.ttl    $B/heritagegraph-nepal.ttl    --content-type "text/turtle; charset=utf-8" --metadata-directive REPLACE
      aws s3 cp $B/heritagegraph-nepal.jsonld $B/heritagegraph-nepal.jsonld --content-type "application/ld+json"        --metadata-directive REPLACE
      aws s3 cp $B/heritagegraph-nepal.nt.gz  $B/heritagegraph-nepal.nt.gz  --content-type "application/gzip"           --metadata-directive REPLACE
      aws s3 cp $B/metadata.json              $B/metadata.json              --content-type "application/json"           --metadata-directive REPLACE
      aws s3 cp $B/checksums.sha256           $B/checksums.sha256           --content-type "text/plain; charset=utf-8"  --metadata-directive REPLACE
      ```

      When uploading future releases, pass `--content-type` the same way.
- [ ] **README and licence in the bucket.** Appendix A recommends a README at the top of the bucket. Upload
      `README.md` and `LICENSE.txt` to the bucket root.
- [ ] **Region.** The handbook asks geospatial datasets to use `us-west-2` unless there is a reason not to. The
      bucket is in `us-east-1`; mention it to the Open Data team so they can say whether that is fine.
- [ ] **Termination protection** on the CloudFormation stack (handbook §5, step 8).
- [ ] **`metadata.json` corrections** for the next release (tracked in HeritageGraphDataset): it counts monuments
      among objects, and lists CC BY 4.0 instead of CC BY-SA 4.0.
