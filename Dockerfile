FROM ruby:3.2-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /srv/jekyll

COPY Gemfile Gemfile.lock ./
RUN bundle install

COPY . .

EXPOSE 5000

CMD ["bundle", "exec", "jekyll", "serve", "--host", "0.0.0.0", "--port", "5000", "--force_polling"]
