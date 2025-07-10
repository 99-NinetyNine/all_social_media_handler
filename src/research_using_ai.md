# Social Media APIs Research Guide

## Week 1 Deliverables

### A. Social Media Platforms to Target

#### Primary Platforms (Week 1-2)
1. **Facebook** - Meta for Business API
2. **Instagram** - Instagram Basic Display API / Instagram Graph API
3. **LinkedIn** - LinkedIn Marketing API
4. **Twitter/X** - Twitter API v2

#### Secondary Platforms (Week 3+)
5. **TikTok** - TikTok for Business API
6. **YouTube** - YouTube Data API v3
7. **Pinterest** - Pinterest API

### B. API Endpoints and Authentication

#### Facebook/Meta API
- **Base URL**: `https://graph.facebook.com/`
- **Authentication**: OAuth 2.0 + App Access Token
- **Key Endpoints**:
  - `/{page-id}/feed` - POST (create), GET (read)
  - `/{page-id}/photos` - POST (upload photos)
  - `/{page-id}/videos` - POST (upload videos)
  - `/{post-id}` - DELETE (delete posts)
- **Rate Limits**: 200 calls per hour per user
- **Required Permissions**: `pages_manage_posts`, `pages_read_engagement`

#### Instagram API
- **Base URL**: `https://graph.instagram.com/`
- **Authentication**: OAuth 2.0 + User Access Token
- **Key Endpoints**:
  - `/{user-id}/media` - POST (create media)
  - `/{media-id}` - GET (media details), DELETE (delete media)
  - `/{user-id}/media_publish` - POST (publish media)
- **Rate Limits**: 240 calls per hour per user
- **Media Types**: IMAGE, VIDEO, CAROUSEL_ALBUM

#### LinkedIn API
- **Base URL**: `https://api.linkedin.com/v2/`
- **Authentication**: OAuth 2.0 + 3-legged auth
- **Key Endpoints**:
  - `/ugcPosts` - POST (create posts)
  - `/shares` - POST (share content)
  - `/assets` - POST (upload media)
- **Rate Limits**: 500 calls per app per day
- **Required Scopes**: `w_member_social`, `r_liteprofile`

#### Twitter API v2
- **Base URL**: `https://api.twitter.com/2/`
- **Authentication**: OAuth 2.0 + Bearer Token
- **Key Endpoints**:
  - `/tweets` - POST (create tweets), DELETE (delete tweets)
  - `/tweets/{id}` - GET (tweet details)
  - `/media/upload` - POST (upload media)
- **Rate Limits**: 300 tweets per 15-minute window
- **Character Limit**: 280 characters

### C. Feature Criteria for Each Platform

#### Content Creation Criteria
| Platform | Text Limit | Image Formats | Video Formats | Max File Size |
|----------|------------|---------------|---------------|---------------|
| Facebook | 63,206 chars | JPG, PNG, GIF | MP4, MOV | 4GB |
| Instagram | 2,200 chars | JPG, PNG | MP4, MOV | 100MB |
| LinkedIn | 3,000 chars | JPG, PNG, GIF | MP4, MOV | 5GB |
| Twitter | 280 chars | JPG, PNG, GIF | MP4, MOV | 512MB |

#### Content Scheduling Criteria
- **Facebook**: Up to 6 months in advance
- **Instagram**: Up to 30 days in advance
- **LinkedIn**: Up to 3 months in advance
- **Twitter**: No native scheduling (use third-party)

#### Analytics Criteria
- **Engagement Metrics**: Likes, comments, shares, reactions
- **Reach Metrics**: Impressions, reach, clicks
- **Conversion Metrics**: Website clicks, lead generation

### D. API Key Management Strategy

#### Development Environment
```bash
# .env file structure
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
INSTAGRAM_APP_ID=your_instagram_app_id
INSTAGRAM_APP_SECRET=your_instagram_app_secret
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
```

#### Production Environment
- Use environment variables
- Implement key rotation strategy
- Use secure vault services (AWS Secrets Manager, Azure Key Vault)
- Implement API key monitoring and alerting

### E. Compliance and Guidelines

#### Data Privacy
- GDPR compliance for EU users
- CCPA compliance for California users
- Platform-specific privacy policies
- User consent management

#### Content Guidelines
- Platform community standards
- Copyright and trademark compliance
- Automated content moderation
- Manual review workflows

## Implementation Priority

### Week 1 Tasks
1. **Day 1-2**: Set up developer accounts for all platforms
2. **Day 3-4**: Create test applications and obtain API keys
3. **Day 5-6**: Test basic API calls using Postman/curl
4. **Day 7**: Document findings and create API testing suite

### Success Metrics
- [ ] Successfully authenticate with all 4 primary platforms
- [ ] Create and delete test posts on each platform
- [ ] Upload and manage media on each platform
- [ ] Retrieve analytics data from each platform
- [ ] Document rate limits and error handling requirements
