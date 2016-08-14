DROP TABLE IF EXISTS
  annotated_text_images,
  tags,
  annotated_tag_images,
  assessment_concepts,
  annotated_assessment_images,
  annotated_query_images,
  images,
  people
CASCADE;

-- images within a chunk are able to be annotated
CREATE TABLE images (
  id  SERIAL PRIMARY KEY,
  name VARCHAR(255),
  data TEXT
);

-- a person is used to identify who annotated an image
CREATE TABLE people (
  id SERIAL PRIMARY KEY,
  alias TEXT,
  email TEXT,
  password TEXT,
  role TEXT DEFAULT 'USER',
  approved BOOLEAN DEFAULT FALSE
);

-- when images get annotated, they are added to these tables

-- text annotations are easy, they just contain a text data type
CREATE TABLE annotated_text_images (
  id SERIAL PRIMARY KEY,
  image_id INT REFERENCES images,
  person_id INT REFERENCES people,
  annotation TEXT
);

-- tag annotations are a little trickier, the annotations are an array of ints from the tags table
-- as tags get added, they get added to the `tags` table, and annotated images store tags as an int array
CREATE TABLE tags (
  id SERIAL PRIMARY KEY,
  value TEXT
);

CREATE TABLE annotated_tag_images (
  id SERIAL PRIMARY KEY,
  image_id INT REFERENCES images,
  person_id INT REFERENCES people,
  annotation TEXT[]
);

-- relevance assessment annotations have a pool of concepts to be judged. Each annotation is a reference to a concept
CREATE TABLE assessment_concepts (
  id SERIAL PRIMARY KEY,
  value TEXT
);

CREATE TABLE annotated_assessment_images (
  id SERIAL PRIMARY KEY,
  image_id INT REFERENCES images,
  person_id INT REFERENCES people,
  annotation INT REFERENCES assessment_concepts
);

-- finally, reverse query annotations are of the same structure as textual annotations
CREATE TABLE annotated_query_images (
  id SERIAL PRIMARY KEY,
  image_id INT REFERENCES images,
  person_id INT REFERENCES people,
  annotation TEXT
);