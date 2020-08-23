from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse
from .models import User, Post, Group


class TestPostsApp(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test_user")
        self.user2 = User.objects.create_user(username="test_user2")
        self.group = Group.objects.create(slug="test_group")

        self.unlogged_client = Client()
        self.logged_client = Client()
        self.logged_client2 = Client()

        self.logged_client.force_login(self.user)
        self.logged_client2.force_login(self.user2)

    def test_create_post_logged(self):
        self.logged_client.post(reverse("new_post"), {"text": "test_text", "group": self.group.pk}, follow=True)
        post = Post.objects.get(author=self.user, text__contains="test_text")

        cache.clear()

        self.assertTrue(self.check_post_content(post, post.text))

    def test_create_post_not_logged(self):
        posts_count_before = Post.objects.count()
        response = self.unlogged_client.post(reverse("new_post"), {"text": "test_text", "group": self.group})
        posts_count_after = Post.objects.count()

        self.assertRedirects(response, f"{reverse('login')}?next={reverse('new_post')}")
        self.assertEqual(posts_count_before, posts_count_after)

    def test_edit_post(self):
        post = Post.objects.create(text="predefined text", author=self.user, group=self.group)
        self.logged_client.post(reverse("post_edit", args=(self.user, post.id)),
                                {"text": "new predefined text", "group": self.group.pk})
        cache.clear()

        post = Post.objects.get(text__contains="predefined text")
        self.assertTrue(self.check_post_content(post, post.text))

    def check_post_content(self, post, content):
        pages = ("index", "profile", "post", "group_posts")
        args = {"index": None,
                "profile": (self.user,),
                "post": (self.user, post.id),
                "group_posts": (self.group.slug,)}
        for page in pages:
            response = self.logged_client.get(reverse(page, args=args[page]))
            self.assertContains(response, content)

        return True

    def test_404(self):
        response = self.unlogged_client.get("/some-nonsense-stuff/")

        self.assertEqual(response.status_code, 404)

    def test_pages_have_img(self):
        with open("media/posts/yt.png", 'rb') as img:
            self.logged_client.post(reverse("new_post"),
                                    {"text": "post with image",
                                     "image": img,
                                     "group": self.group.pk})
        cache.clear()

        post = Post.objects.get(text__contains="post with image")
        img_tag = "<img class=\"card-img\""

        self.assertTrue(self.check_post_content(post, img_tag))

    def test_wrong_img_format(self):
        with open("requirements.txt") as img:
            response = self.logged_client.post(
                reverse("new_post"),
                {
                    "text": "post with non graphical file",
                    "image": img
                }
            )
        msg = "Загрузите правильное изображение. Файл, который вы загрузили, поврежден или не является изображением."

        self.assertContains(response, msg)

    def test_cached_index_page(self):
        post_1 = Post.objects.create(author=self.user, text="post_1")
        response = self.logged_client.get(reverse("index"))
        self.assertContains(response, post_1.text)

        post_2 = Post.objects.create(author=self.user, text="post_2")
        response = self.logged_client.get(reverse("index"))
        self.assertNotContains(response, post_2.text)

        cache.clear()

        response = self.logged_client.get(reverse("index"))
        self.assertContains(response, post_1.text)
        self.assertContains(response, post_2.text)

    def test_follow_unfollow(self):
        followers_count_before = self.user2.following.count()
        self.logged_client.get(reverse("profile_follow", args=(self.user2,)))
        followers_count_after = self.user2.following.count()

        self.assertEqual(followers_count_after, followers_count_before + 1)

        followers_count_before = self.user2.following.count()
        self.logged_client.get(reverse("profile_unfollow", args=(self.user2,)))
        followers_count_after = self.user2.following.count()

        self.assertEqual(followers_count_after + 1, followers_count_before)

    def test_new_post_in_feed(self):
        post = Post.objects.create(author=self.user2, text="text for followers")
        response = self.logged_client.get(reverse("follow_index"))
        self.assertNotContains(response, post.text)

        self.logged_client.get(reverse("profile_follow", args=(self.user2,)))
        response = self.logged_client.get(reverse("follow_index"))
        self.assertContains(response, post.text)

    def test_comment(self):
        comment_text = "just a comment"
        post = Post.objects.create(author=self.user2, text="post for comments")
        self.logged_client.post(reverse("add_comment", args=(self.user2, post.id)),
                                {"text": comment_text})
        response = self.logged_client.get(reverse("post", args=(self.user2,  post.id)))
        self.assertContains(response, comment_text)

        response = self.unlogged_client.post(reverse("add_comment", args=(self.user2.username, post.id)),
                                             {"text": comment_text})
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('add_comment', args=(self.user2, post.id))}")
