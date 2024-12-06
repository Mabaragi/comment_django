COMMENT_QUERY = """
    query commentList($commentListInput: CommentListInput!) {
      commentList(commentListInput: $commentListInput) {
        ...CommentList
      }
    }
    
    fragment CommentList on CommentList {
      isEnd
      totalCount
      bestTotalCount
      selectedSortOpt {
        id
        name
        param
      }
      sortOptList {
        id
        name
        param
      }
      commentList {
        ...CommentItem
      }
    }
    
    fragment CommentItem on CommentItem {
      parentUid
      userUid
      productId
      seriesId
      comment
      likeCount
      replyCount
      createDt
      commentType
      commentUid
      title
      hidden
      isBest
      blocked
      commentStatus
      deleted
      expose
      myReplyCount
      userThumbnailUrl
      userName
      liked
      emoticon {
        itemSubType
        resourceId
        itemId
        itemVer
      }
      isSpoiler
    }
    """

EPISODE_QUERY = """
    query contentHomeProductList($after: String, $before: String, $first: Int, $last: Int, $seriesId: Long!, $boughtOnly: Boolean, $sortType: String) {
      contentHomeProductList(
        seriesId: $seriesId
        after: $after
        before: $before
        first: $first
        last: $last
        boughtOnly: $boughtOnly
        sortType: $sortType
      ) {
        totalCount
        pageInfo {
          hasNextPage
          endCursor
          hasPreviousPage
          startCursor
        }
        selectedSortOption {
          id
          name
          param
        }
        sortOptionList {
          id
          name
          param
        }
        edges {
          cursor
          node {
            ...SingleListViewItem
          }
        }
      }
    }
    
    fragment SingleListViewItem on SingleListViewItem {
      id
      type
      thumbnail
      showPlayerIcon
      isCheckMode
      isChecked
      scheme
      row1
      row2
      row3 {
        badgeList
        text
        priceList
      }
      single {
        productId
        ageGrade
        id
        isFree
        thumbnail
        title
        slideType
        operatorProperty {
          isTextViewer
        }
      }
      isViewed
      eventLog {
        ...EventLogFragment
      }
      discountRate
      discountRateText
    }
    
    
    fragment EventLogFragment on EventLog {
      fromGraphql
      click {
        layer1
        layer2
        setnum
        ordnum
        copy
        imp_id
        imp_provider
      }
      eventMeta {
        id
        name
        subcategory
        category
        series
        provider
        series_id
        type
      }
      viewimp_contents {
        type
        name
        id
        imp_area_ordnum
        imp_id
        imp_provider
        imp_type
        layer1
        layer2
      }
      customProps {
        landing_path
        view_type
        helix_id
        helix_yn
        helix_seed
        content_cnt
        event_series_id
        event_ticket_type
        play_url
        banner_uid
      }
    }
    """
