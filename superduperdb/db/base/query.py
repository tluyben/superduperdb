from __future__ import annotations

import typing as t
from abc import ABC, abstractmethod

from superduperdb.container.serializable import Serializable

if t.TYPE_CHECKING:
    from superduperdb.container.model import Model
    from superduperdb.db.base.datalayer import Datalayer


class SelectOne(ABC, Serializable):
    """
    Base class for queries which return a single line/ record of data
    """

    @abstractmethod
    def __call__(self, db: Datalayer):
        pass


class Like(ABC, Serializable):
    """
    Base class for queries which invoke vector-search
    """

    @abstractmethod
    def __call__(self, db: Datalayer):
        pass


class Select(ABC, Serializable):
    """
    Abstract base class, encapsulating Select database queries/ db reads.
    This allows the concrete implementation of each db to differ substantially on
    stored properties necessary for Serializableing the DB.
    """

    @property
    def select_table(self) -> 'Select':
        """Return a query that selects this table"""
        raise NotImplementedError

    def is_trivial(self) -> bool:
        """Determines when a select statement is "just" select everything.

        For example, in SQL: "FROM my_table SELECT *"
        For example, in MongoDB: "collection.find()"
        """
        raise NotImplementedError

    def select_ids(self) -> 'Select':
        """Converts the Serializable into a Serializable which only returns the id
        of each column/ document.
        """
        raise NotImplementedError

    def select_using_ids(self, ids: t.Sequence[str]) -> t.Any:
        """Create a select using the same Serializable, subset to the specified ids

        :param ids: string ids to which subsetting should occur
        """
        pass

    def add_fold(self, fold: str) -> 'Select':
        """Create a select which selects the same data, but additionally restricts to
        the fold specified

        :param fold: possible values {'train', 'valid'}
        """
        raise NotImplementedError

    def model_update(
        self,
        db: Datalayer,
        ids: t.Sequence[t.Any],
        key: str,
        model: Model,
        outputs: t.Sequence[t.Any],
    ) -> None:
        """
        Add outputs of ``model`` to the db ``db``.

        :param db: db
        :param model: model identifier to be updated against
        :param key: key on which model was applied
        :param outputs: (encoded) outputs to be added
        :param ids: ids of input documents corresponding to each output
        """
        raise NotImplementedError

    @abstractmethod
    def __call__(self, db: Datalayer):
        """
        Apply Serializable to db

        :param db: db instance
        """
        pass


class Insert(ABC, Serializable):
    """
    Base class for database inserts.

    :param refresh: toggle to ``False`` to suppress job triggering
                    (model computations on new docs)
    :param verbose: toggle tp ``False`` to suppress/reduce stdout
    :param documents: list of documents to insert

    """

    # must implement attribute/ property self.documents
    documents: t.List

    @property
    @abstractmethod
    def table(self) -> str:
        """Extracts the table collection from the object"""

    @property
    @abstractmethod
    def select_table(self) -> Select:
        """Returns a Select object which selects the table into which the insert
        was inserted"""

    @abstractmethod
    def __call__(self, db: Datalayer):
        """
        Apply Serializable to db

        :param db: db instance
        """
        pass


class Delete(ABC, Serializable):
    """
    Base class for deleting documents from db
    """

    @abstractmethod
    def __call__(self, db: Datalayer):
        """
        Apply Serializable to db

        :param db: db instance
        """
        pass


class Update(ABC, Serializable):
    """
    Base class for database updates.

    :param refresh: toggle to ``False`` to suppress job triggering
                    (model computations on new docs)
    :param verbose: toggle tp ``False`` to suppress/reduce stdout

    """

    @property
    def select_table(self) -> Select:
        """Returns a Select object which selects the table into which the insert
        was inserted
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def select(self) -> Select:
        """Converts the update object to a Select object, which selects where
        the update was made.
        """

    @property
    def select_ids(self) -> Select:
        """
        Converts the update object to a Select object, which selects where
        the update was made, and returns only ids.
        """
        raise NotImplementedError

    @abstractmethod
    def __call__(self, db: Datalayer):
        """
        Apply Serializable to db.

        :param db: db instance
        """
        pass