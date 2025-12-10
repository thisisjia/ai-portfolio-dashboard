# Building a Chatbot Framework

## Critical System Features

1. **Workflow Enforcement**: Portfolio Performance Assistant won't skip steps
2. **Citation Merging**: Combines sources from all tools into final response
3. **Deep Research Detection**: Manages expectations for 2-3 minute queries
4. **Format Requirements**: Client-specific bullet formats for reports
5. **Cache Management**: `EnhancedReportCache` prevents redundant API calls

## Frontend Integration

- **SSE Streaming**: Real-time response streaming
- **Module Types**: "investmentTracker" vs "investments" for different contexts
- **Message Filtering**: Removes verbose assistant messages on investment page

## Why This Architecture?

1. **Scalability**: Add new assistants without breaking existing ones
2. **Maintainability**: Each assistant has clear boundaries
3. **User Experience**: Progressive disclosure of complexity
4. **Performance**: Parallel tool execution where possible
5. **Compliance**: Full audit trail of all decisions

## To Recreate This System:

1. **Start with State**: Define your state structure first
2. **Build Router**: Create primary assistant that understands all query types
3. **Add Specialists**: One assistant per major use case
4. **Implement Tools**: Separate tools for data access vs intelligence
5. **Response Formatting**: Dedicated assistant for output consistency
6. **Graph Assembly**: Connect with proper entry/exit nodes
7. **Test Workflows**: Ensure multi-step processes complete properly

The key insight: **Each assistant should do ONE thing excellently** rather than many things adequately. The router's job is to pick the right expert for each query.